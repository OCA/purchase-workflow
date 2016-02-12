# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class Procurement(models.Model):
    _inherit = 'procurement.order'

    request_id = fields.Many2one('purchase.request',
                                 string='Latest Purchase Request')

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['request_id'] = False
        return super(Procurement, self).copy(default)

    @api.model
    def _prepare_purchase_request_line(self, purchase_request_id, procurement):
        return {
            'product_id': procurement.product_id.id,
            'name': procurement.product_id.name,
            'date_required': procurement.date_planned,
            'product_uom_id': procurement.product_uom.id,
            'product_qty': procurement.product_qty,
            'request_id': purchase_request_id,
        }

    @api.model
    def _get_warehouse(self, procurement):
        """
            Return the warehouse containing the procurment stock location
            (or one of it ancestors)
            If none match, returns then first warehouse of the company
        """
        warehouse_obj = self.env['stock.warehouse']
        warehouses = warehouse_obj.search([('company_id', '=',
                                            procurement.company_id.id)])
        if warehouses:
            return warehouses[0].id
        else:
            return False

    @api.model
    def _prepare_purchase_request(self, procurement):

        return {
            'origin': procurement.origin,
            'company_id': procurement.company_id.id,
            'warehouse_id': self._get_warehouse(procurement),
        }

    @api.model
    def _search_existing_purchase_request(self, procurement):
        """This method is to be implemented by other modules that can
        provide a criteria to select the appropriate purchase request to be
        extended.
        """
        return False

    @api.model
    def _run(self, procurement):
        request_obj = self.env['purchase.request']
        request_line_obj = self.env['purchase.request.line']
        if procurement.rule_id and procurement.rule_id.action == 'buy' \
                and procurement.product_id.purchase_request:
            # Search for an existing Purchase Request to be considered
            # to be extended.
            pr = self._search_existing_purchase_request(procurement)
            if not pr:
                request_data = self._prepare_purchase_request(procurement)
                req = request_obj.create(request_data)
                procurement.message_post(body=_("Purchase Request created"))
                procurement.request_id = req.id
            request_line_data = self._prepare_purchase_request_line(
                pr, procurement)
            request_line_obj.create(request_line_data),
            self.message_post([procurement.id],
                              body=_("Purchase Request extended."))
            return True
        return super(Procurement, self)._run(procurement)
