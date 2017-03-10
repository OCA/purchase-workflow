# -*- coding: utf-8 -*-
# Copyright 2016-2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    request_id = fields.Many2one(
        comodel_name='purchase.request',
        ondelete='restrict',
        string='Latest Purchase Request',
        copy=False,
    )

    @api.model
    def _prepare_purchase_request_line(self, purchase_request, procurement):
        return {
            'product_id': procurement.product_id.id,
            'name': procurement.product_id.name,
            'date_required': procurement.date_planned,
            'product_uom_id': procurement.product_uom.id,
            'product_qty': procurement.product_qty,
            'request_id': purchase_request.id,
            'procurement_id': procurement.id
        }

    @api.model
    def _prepare_purchase_request(self, procurement):
        return {
            'origin': procurement.origin,
            'company_id': procurement.company_id.id,
            'picking_type_id': procurement.rule_id.picking_type_id.id,
        }

    @api.model
    def _search_existing_purchase_request(self, procurement):
        """
        This method is to be implemented by other modules that can
        provide a criteria to select the appropriate purchase request to be
        extended.
        :param procurement: procurement.order object
        :return: False
        """
        return False

    @api.multi
    def _run(self):
        self.ensure_one()
        purchase_request_model = self.env['purchase.request']
        purchase_request_line_model = self.env['purchase.request.line']
        if self.rule_id and self.rule_id.action == 'buy' \
                and self.product_id.purchase_request:
            # Search for an existing Purchase Request to be considered
            # to be extended.
            pr = self._search_existing_purchase_request(self)
            if not pr:
                request_data = self._prepare_purchase_request(self)
                req = purchase_request_model.create(request_data)
                self.message_post(body=_("Purchase Request created"))
                self.request_id = req
            request_line_data = self._prepare_purchase_request_line(req, self)
            purchase_request_line_model.create(request_line_data),
            self.message_post(body=_("Purchase Request extended."))
            return True
        return super(ProcurementOrder, self)._run()

    @api.multi
    def propagate_cancels(self):
        result = super(ProcurementOrder, self).propagate_cancels()
        # Remove the reference to the request_id from the procurement order
        for procurement in self:
            request = procurement.request_id
            procurement.request_id = False
            # Search for purchase request lines containing the procurement_id
            request_lines = self.env['purchase.request.line'].search(
                [('procurement_id', '=', procurement.id)])
            # Remove the purchase request lines, if the request is not draft
            # or reject, otherwise, raise ValidationError
            if any(l.request_id.state not in ('draft', 'reject')
                   for l in request_lines):
                raise ValidationError(_(
                    "Cannot cancel this procurement as the related "
                    "purchase request is in progress confirmed already. "
                    "Please cancel the purchase request first."
                ))
            else:
                request_lines.unlink()
            # If the purchase request has no line, delete it as well
            if len(request.line_ids) == 0:
                request.unlink()
        return result
