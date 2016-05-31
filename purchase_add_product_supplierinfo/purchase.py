# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _check_product_supplierinfo(self):
        lines = []
        for line in self.order_line:
            suppinfo = self.env['product.supplierinfo'].search([
                ('product_id', '=', line.product_id.id),
                ('name', '=', self.partner_id.id)])
            if not suppinfo:
                lines.append((0, 0, {
                    'name': line.name,
                    'product_id': line.product_id.id,
                }))
        return lines

    @api.multi
    def purchase_confirm(self):
        self.ensure_one()
        lines_for_update = self._check_product_supplierinfo()
        if lines_for_update:
            if self.partner_id.parent_id:
                supplier_id = self.partner_id.parent_id
            else:
                supplier_id = self.partner_id
            ctx = dict(
                default_wizard_line_ids=lines_for_update,
            )
            add_supplierinfo_form = self.env.ref(
                'purchase_add_product_supplierinfo.'
                'view_purchase_add_supplierinfo_form', False)
            return {
                'name': _("Associate the supplier '%s' with the products "
                          "of this purchase order.") % supplier_id.name,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.add.product.supplierinfo',
                'views': [(add_supplierinfo_form.id, 'form')],
                'view_id': add_supplierinfo_form.id,
                'target': 'new',
                'context': ctx,
            }
        else:
            self.signal_workflow('purchase_confirm')
