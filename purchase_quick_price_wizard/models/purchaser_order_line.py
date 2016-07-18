# -*- coding: utf-8 -*-
# Florent de Labarre - 2016

from openerp import api, models, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def action_view_supplier_price(self, context=None):
        view_id = self.env.ref('purchase_quick_price_wizard.product_supplierinfo_tree_view').id
        return {
            'name': _('Product price : %s - %s' % (self.product_id.product_tmpl_id.default_code, self.product_id.product_tmpl_id.name)),
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree'), (False, 'form')],
            'res_model': 'product.supplierinfo',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': "[('product_tmpl_id','=', %d)]" % self.product_id.product_tmpl_id.id
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
