# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    only_allowed_products = fields.Boolean(
        string="Use only allowed products",
        help="If checked, only the products provided by this supplier "
             "will be shown.")
    allowed_products = fields.Many2many(
        comodel_name='product.product', string='Allowed products')

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        result = super(AccountInvoice, self).onchange_partner_id(
            type=type, partner_id=partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        partner = self.env['res.partner'].browse(partner_id)
        result['value']['only_allowed_products'] = (
            partner.commercial_partner_id.supplier_invoice_only_allowed)
        return result

    @api.multi
    @api.onchange('only_allowed_products')
    def onchange_only_allowed_products(self):
        self.ensure_one()
        product_obj = self.env['product.product']
        self.allowed_products = product_obj.search(
            [('purchase_ok', '=', True)])
        if self.only_allowed_products and self.partner_id:
            cond = self._prepare_allowed_product_domain()
            supplierinfos = self.env['product.supplierinfo'].search(cond)
            self.allowed_products = product_obj.search(
                [('product_tmpl_id', 'in',
                  [x.product_tmpl_id.id for x in supplierinfos])])

    def _prepare_allowed_product_domain(self):
        return [('name', 'in', (self.partner_id.commercial_partner_id.id,
                                self.partner_id.id))]
