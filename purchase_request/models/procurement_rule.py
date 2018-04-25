# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.model
    def _prepare_purchase_request_line(self, request_id, product_id,
                                       product_qty, product_uom, values):
        procurement_uom_po_qty = product_uom._compute_quantity(
            product_qty, product_id.uom_po_id)
        return {
            'product_id': product_id.id,
            'name': product_id.name,
            'date_required': 'date_planned' in values
            and values['date_planned'] or fields.Datetime.now(),
            'product_uom_id': product_id.uom_po_id.id,
            'product_qty': procurement_uom_po_qty,
            'request_id': request_id.id,
            'move_dest_ids': [(4, x.id)
                              for x in values.get('move_dest_ids', [])],
            'orderpoint_id': values.get('orderpoint_id', False) and values.get(
                'orderpoint_id').id,
        }

    @api.model
    def _prepare_purchase_request(self, origin, values):
        gpo = self.group_propagation_option
        group_id = (gpo == 'fixed' and self.group_id.id) or \
                   (gpo == 'propagate' and values['group_id'].id) or False
        return {
            'origin': origin,
            'company_id': values['company_id'].id,
            'picking_type_id': self.picking_type_id.id,
            'group_id': group_id or False,
        }

    @api.model
    def _make_pr_get_domain(self, values):
        """
        This method is to be implemented by other modules that can
        provide a criteria to select the appropriate purchase request to be
        extended.
        :return: False
        """
        domain = (
            ('state', '=', 'draft'),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('company_id', '=', values['company_id'].id),
        )
        gpo = self.group_propagation_option
        group_id = (gpo == 'fixed' and self.group_id.id) or \
                   (gpo == 'propagate' and values['group_id'].id) or False
        if group_id:
            domain += (
                ('group_id', '=', group_id),
                )
        return domain

    @api.multi
    def is_create_purchase_request_allowed(self, product_id):
        """
        Tell if current procurement order should
        create a purchase request or not.
        :return: boolean
        """
        return self.action == 'buy' \
            and product_id.purchase_request

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom,
                 location_id, name, origin, values):
        if self.is_create_purchase_request_allowed(product_id):
            self.create_purchase_request(product_id, product_qty,
                                         product_uom, origin, values)
            return
        return super(ProcurementRule, self)._run_buy(
            product_id, product_qty, product_uom, location_id, name,
            origin, values)

    @api.multi
    def create_purchase_request(self, product_id, product_qty, product_uom,
                                origin, values):
        """
        Create a purchase request containing procurement order product.
        """
        purchase_request_model = self.env['purchase.request']
        purchase_request_line_model = self.env['purchase.request.line']
        cache = {}
        pr = self.env['purchase.request']
        domain = self._make_pr_get_domain(values)
        if domain in cache:
            pr = cache[domain]
        elif domain:
            pr = self.env['purchase.request'].search([dom for dom in domain])
            pr = pr[0] if pr else False
            cache[domain] = pr
        if not pr:
            request_data = self._prepare_purchase_request(origin, values)
            pr = purchase_request_model.create(request_data)
            cache[domain] = pr
        elif not pr.origin or origin not in pr.origin.split(', '):
            if pr.origin:
                if origin:
                    pr.write({'origin': pr.origin + ', ' + origin})
                else:
                    pr.write({'origin': pr.origin})
            else:
                pr.write({'origin': origin})
        # Create Line
        request_line_data = self._prepare_purchase_request_line(
            pr, product_id, product_qty, product_uom, values)
        purchase_request_line_model.create(request_line_data)
