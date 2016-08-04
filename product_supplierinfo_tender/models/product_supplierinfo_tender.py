# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp import _, api, fields, models
import openerp.addons.decimal_precision as dp

_STATES = [('draft', 'Draft'), ('open', 'Call for Bids'),
           ('selection', 'Bid Selection'), ('done', 'Completed'),
           ('cancel', 'Cancelled')]


PREPARATION_STATES = {
    'open': [('readonly', True)],
    'selection': [('readonly', True)],
    'done': [('readonly', True)],
    'cancel': [('readonly', True)],
}
SELECTION_STATES = {
    'selection': [('readonly', True)],
    'done': [('readonly', True)],
    'cancel': [('readonly', True)],
}


class ProductSupplierinfoTender(models.Model):
    _name = "product.supplierinfo.tender"
    _description = "Supplier Pricelist Tender"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string='Reference', required=True, copy=False,
                       default='New', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('open', 'Call for Bids'),
                              ('selection', 'Bid Selection'),
                              ('done', 'Completed'),
                              ('cancel', 'Cancelled')],
                             string='Status', select=True,
                             copy=False, default='draft',
                             track_visibility='onchange')
    date_end = fields.Datetime(string='Tender Closing Deadline', copy=False)
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  states=PREPARATION_STATES,
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    description = fields.Text(string='Description')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        select=1, states=PREPARATION_STATES,
        default=lambda self: self.env.user.company_id.id)
    line_ids = fields.One2many(
        comodel_name='product.supplierinfo.tender.line',
        inverse_name='tender_id',
        string='Tender Lines',
        states=SELECTION_STATES,
        copy=True)
    bid_ids = fields.One2many(
        comodel_name='product.supplierinfo.bid',
        inverse_name='tender_id',
        string='Bids',
        states=SELECTION_STATES,
        readonly=True,
        copy=False)
    product_supplierinfo_ids = fields.One2many(
        comodel_name='product.supplierinfo',
        inverse_name='tender_id',
        string='Supplier Pricelists',
        states=PREPARATION_STATES,
        copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'product.supplierinfo.tender') or '/'
        return super(ProductSupplierinfoTender, self).create(vals)

    @api.multi
    def button_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.bid_ids.button_open()

    @api.multi
    def button_open(self):
        for rec in self:
            rec.state = 'open'

    @api.multi
    def button_selection(self):
        for rec in self:
            rec.state = 'selection'
            rec.bid_ids.button_close()

    @api.multi
    def button_done(self):
        for rec in self:
            rec.state = 'done'

    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def _prepare_bid(self, tender, supplier):
        return {
            'partner_id': supplier.id,
            'currency_id': tender.currency_id.id,
            'tender_id': tender.id
        }

    @api.model
    def _prepare_supplierinfo(self, tender, line, bid_id, supplier):
        return {
            'bid_id': bid_id,
            'name': supplier.id,
            'product_tmpl_id': line.product_id.product_tmpl_id.id,
            'product_id': line.product_id.id,
            'company_id': tender.company_id.id,
            'currency_id': tender.currency_id.id,
            'min_qty': line.min_qty
        }

    @api.multi
    def make_bid(self, partner_id):
        assert partner_id, 'Vendor should be specified'
        bid_model = self.env['product.supplierinfo.bid']
        supplierinfo_model = self.env['product.supplierinfo']
        partner_model = self.env['res.partner']
        supplier = partner_model.browse(partner_id)
        res = {}
        for tender in self:
            bid = bid_model.create(self._prepare_bid(tender, supplier))
            bid.message_post(body=_("Bid created"))
            res[tender.id] = bid.id
            for line in tender.line_ids:
                supplierinfo_model.create(self._prepare_supplierinfo(
                    tender, line, bid.id, supplier))
        return res


class ProductSupplierinfoTenderLine(models.Model):
    _name = "product.supplierinfo.tender.line"
    _description = "Supplier Pricelist Tender Line"

    tender_id = fields.Many2one(string='Tender',
                                comodel_name='product.supplierinfo.tender',
                                copy=False)
    product_id = fields.Many2one('product.product',
                                 string='Product',
                                 domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)
    product_uom_id = fields.Many2one(related='product_id.uom_id',
                                     string='Product Unit of Measure')
    min_qty = fields.Float(string='Minimum Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), default=1)
