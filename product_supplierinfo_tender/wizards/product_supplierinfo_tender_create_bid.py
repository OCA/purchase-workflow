# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import UserError, ValidationError


class ProductSupplierinfoTenderCreateBid(models.TransientModel):
    _name = "product.supplierinfo.tender.create.bid"
    _description = "Product Supplierinfo Tender Create Bid"

    partner_ids = fields.Many2many('res.partner',
                                   'product_supplierinfo_tender_supplier_rel',
                                   'tender_id', 'partner_id',
                                   string='Vendors', required=True,
                                   domain=[('supplier', '=', True)])

    @api.model
    def default_get(self, fields):
        res = super(ProductSupplierinfoTenderCreateBid, self).default_get(
            fields)
        tender_ids = self.env.context['active_ids'] or []
        if not tender_ids:
            return res
        active_model = self.env.context['active_model']
        assert active_model == 'product.supplierinfo.tender', \
            'Bad context propagation'
        for tender in self.env['product.supplierinfo.tender'].browse(
                tender_ids):
            if not tender.line_ids:
                raise UserError(
                    _('Define product(s) you want to include in the '
                      'call for tenders %s.') % tender.name)
        return res

    @api.multi
    def create_bid(self):
        tender_ids = self.env.context['active_ids'] or []
        tender_obj = self.env['product.supplierinfo.tender']
        for wizard in self:
            for partner_id in wizard.partner_ids:
                tenders = tender_obj.browse(tender_ids)
                tenders.make_bid(partner_id.id)
        return {'type': 'ir.actions.act_window_close'}
