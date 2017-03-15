# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class Procurement(models.Model):
    _inherit = 'procurement.order'

    request_id = fields.Many2one('purchase.request',
                                 ondelete='restrict',
                                 string='Latest Purchase Request')

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        self.ensure_one()
        default['request_id'] = False
        return super(Procurement, self).copy(default)

    @api.model
    def _prepare_purchase_request_line(self, purchase_request):
        return {
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'date_required': self.date_planned,
            'product_uom_id': self.product_uom.id,
            'product_qty': self.product_qty,
            'request_id': purchase_request.id,
            'procurement_id': self.id
        }

    @api.model
    def _prepare_purchase_request(self):
        return {
            'origin': self.origin,
            'company_id': self.company_id.id,
            'picking_type_id': self.rule_id.picking_type_id.id,
        }

    @api.model
    def _search_existing_purchase_request(self):
        """This method is to be implemented by other modules that can
        provide a criteria to select the appropriate purchase request to be
        extended.
        """
        return False

    @api.model
    def _run(self):
        request_obj = self.env['purchase.request']
        request_line_obj = self.env['purchase.request.line']
        if self.rule_id and self.rule_id.action == 'buy' \
                and self.product_id.purchase_request:
            # Search for an existing Purchase Request to be considered
            # to be extended.
            pr = self._search_existing_purchase_request()
            if not pr:
                request_data = self._prepare_purchase_request()
                req = request_obj.create(request_data)
                self.message_post(body=_("Purchase Request created"))
                self.request_id = req.id
            request_line_data = self._prepare_purchase_request_line(
                req)
            request_line_obj.create(request_line_data),
            self.message_post(body=_("Purchase Request extended."))
            return True
        return super(Procurement, self)._run()

    @api.multi
    def propagate_cancels(self):
        result = super(Procurement, self).propagate_cancels()
        # Remove the reference to the request_id from the procurement order
        for procurement in self:
            request = procurement.request_id
            procurement.write({'request_id': None})
            # Search for purchase request lines containing the procurement_id
            request_lines = self.env['purchase.request.line'].\
                search([('procurement_id', '=', procurement.id)])
            # Remove the purchase request lines, if the request is not draft
            # or reject
            for line in request_lines:
                if line.request_id.state not in ('draft', 'reject'):
                    raise ValidationError(_('Can not cancel this procurement '
                                            'as the related purchase request '
                                            'is in progress confirmed already.'
                                            ' Please cancel the purchase'
                                            ' request first.'))
                else:
                    line.unlink()
            # If the purchase request has not lines, delete it as well
            if len(request.line_ids) == 0:
                request.unlink()
        return result
