# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_manage_variants(self):
        self.ensure_one()
        # active_model_name = self.env.context.get('active_model')
        # XXX: managed by `default_` in context
        # vals = {}
        # if active_model_name == 'purchase.order.line':
        # same as using the field here -- those are next to useless,
        # according to Simone - and I can't say that I think otherwise
        # vals['default_template_id'] = self.product_id.product_tmpl_id.id

        # wiz = self.env['purchase.manage.variant'].create(vals)
        ctx_params = self.env.context.get('params', {})
        active_model = ctx_params.get('model')
        active_id = ctx_params.get('id')
        if active_model == 'purchase.order.line':
            order_id = self.env['purchase.order.line'].browse(
                active_id).order_id.id
        elif active_model == 'purchase.order':
            order_id = active_id
        else:
            return

        wiz = self.env['purchase.manage.variant'].create({
            'purchase_order_id': order_id,
        })
        wiz._onchange_product_tmpl_id()

        return {
            'name': _('Modify Variants'),
            'src_model': active_model,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'purchase.manage.variant',
            'res_id': wiz.id,
            'type': 'ir.actions.act_window',
        }
