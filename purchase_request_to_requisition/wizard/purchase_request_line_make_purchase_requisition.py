# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import openerp.addons.decimal_precision as dp
from openerp import api, exceptions, fields, models
from openerp.tools.translate import _


class PurchaseRequestLineMakePurchaseRequisition(models.TransientModel):
    _name = "purchase.request.line.make.purchase.requisition"
    _description = "Purchase Request Line Make Purchase Requisition"

    item_ids = fields.One2many(
        'purchase.request.line.make.purchase.requisition.item',
        'wiz_id', string='Items')
    purchase_requisition_id = fields.Many2one(
        'purchase.requisition', string='Purchase Requisition',
        required=False, domain=[('state', '=', 'draft')])

    @api.model
    def _prepare_item(self, line):
        return {
            'line_id': line.id,
            'request_id': line.request_id.id,
            'product_id': line.product_id.id,
            'name': line.name or line.product_id.name,
            'product_qty': line.product_qty,
            'product_uom_id': line.product_uom_id.id,
        }

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRequestLineMakePurchaseRequisition,
                    self).default_get(fields)
        request_line_obj = self.env['purchase.request.line']
        request_line_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if not request_line_ids:
            return res
        assert active_model == 'purchase.request.line', \
            'Bad context propagation'

        items = []
        for line in request_line_obj.browse(request_line_ids):
            items.append([0, 0, self._prepare_item(line)])
        res['item_ids'] = items
        return res

    @api.model
    def _prepare_purchase_requisition(self, picking_type_id,
                                      company_id):
        data = {
            'origin': '',
            'picking_type_id': picking_type_id,
            'company_id': company_id,
            }
        return data

    @api.model
    def _prepare_purchase_requisition_line(self, pr, item):
        return {
            'requisition_id': pr.id,
            'product_qty': item.product_qty,
            'product_id': item.product_id.id,
            'product_uom_id': item.product_uom_id.id,
            'purchase_request_lines': [(4, item.line_id.id)],
            'account_analytic_id': item.line_id.analytic_account_id.id or
            False,
        }

    @api.model
    def _get_requisition_line_search_domain(self, requisition, item):
        vals = [('requisition_id', '=', requisition.id),
                ('product_id', '=', item.product_id.id or False),
                ('product_uom_id', '=',
                 item.product_uom_id.id or False),
                ('account_analytic_id', '=',
                 item.line_id.analytic_account_id.id or False)]
        return vals

    @api.multi
    def make_purchase_requisition(self):
        pr_obj = self.env['purchase.requisition']
        pr_line_obj = self.env['purchase.requisition.line']
        company_id = False
        picking_type_id = False
        requisition = False
        res = []
        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise exceptions.Warning(
                    _('Enter a positive quantity.'))
            line_company_id = line.company_id \
                and line.company_id.id or False
            if company_id is not False \
                    and line_company_id != company_id:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same company.'))
            else:
                company_id = line_company_id

            line_picking_type = line.request_id.picking_type_id
            if picking_type_id is not False \
                    and line_picking_type.id != picking_type_id:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same picking type.'))
            else:
                picking_type_id = line_picking_type.id

            if self.purchase_requisition_id:
                requisition = self.purchase_requisition_id
            if not requisition:
                preq_data = self._prepare_purchase_requisition(picking_type_id,
                                                               company_id)
                requisition = pr_obj.create(preq_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_requisition_line_search_domain(requisition,
                                                              item)
            available_pr_lines = pr_line_obj.search(domain)
            if available_pr_lines:
                pr_line = available_pr_lines[0]
                new_qty = pr_line.product_qty + item.product_qty
                pr_line.product_qty = new_qty
                pr_line.purchase_request_lines = [(4, line.id)]
            else:
                po_line_data = self._prepare_purchase_requisition_line(
                    requisition, item)
                pr_line_obj.create(po_line_data)
            res.append(requisition.id)

        return {
            'domain': "[('id','in', ["+','.join(map(str, res))+"])]",
            'name': _('Purchase requisition'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }


class PurchaseRequestLineMakePurchaseRequisitionItem(models.TransientModel):
    _name = "purchase.request.line.make.purchase.requisition.item"
    _description = "Purchase Request Line Make Purchase Requisition Item"

    wiz_id = fields.Many2one(
        'purchase.request.line.make.purchase.requisition',
        string='Wizard', required=True, ondelete='cascade',
        readonly=True)
    line_id = fields.Many2one('purchase.request.line',
                              string='Purchase Request Line',
                              required=True,
                              readonly=True)
    request_id = fields.Many2one('purchase.request',
                                 related='line_id.request_id',
                                 string='Purchase Request',
                                 readonly=True)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description', required=True)
    product_qty = fields.Float(string='Quantity to Bid',
                               digits_compute=dp.get_precision('Product UoS'))
    product_uom_id = fields.Many2one('product.uom', string='UoM')

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
