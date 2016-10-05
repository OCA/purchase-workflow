# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

import openerp.addons.decimal_precision as dp
from openerp import _, api, exceptions, fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _name = "purchase.request.line.make.purchase.order"
    _description = "Purchase Request Line Make Purchase Order"

    supplier_id = fields.Many2one('res.partner', string='Supplier',
                                  required=False,
                                  domain=[('supplier', '=', True)])
    item_ids = fields.One2many(
        'purchase.request.line.make.purchase.order.item',
        'wiz_id', string='Items')
    purchase_order_id = fields.Many2one('purchase.order',
                                        string='Purchase Order',
                                        required=False,
                                        domain=[('state', '=', 'draft')])

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
    def _check_valid_request_line(self, request_line_ids):
        location = False
        picking_type = False
        company_id = False

        for line in self.env['purchase.request.line'].browse(request_line_ids):

            if line.request_id.state != 'approved':
                raise exceptions.Warning(
                    _('Purchase Request %s is not approved') %
                    line.request_id.name)

            if line.purchase_state == 'done':
                raise exceptions.Warning(
                    _('The purchase has already been completed.'))

            line_company_id = line.company_id \
                and line.company_id.id or False
            if company_id is not False \
                    and line_company_id != company_id:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same company.'))
            else:
                company_id = line_company_id

            line_picking_type = line.request_id.picking_type_id or False
            if not line_picking_type:
                raise exceptions.Warning(
                    _('You have to enter a Picking Type.'))
            if picking_type is not False \
                    and line_picking_type != picking_type:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same Picking Type.'))
            else:
                picking_type = line_picking_type

            line_location = line.procurement_id and \
                line.procurement_id.location_id or False

            if location is not False and line_location != location and \
                    line_location:
                raise exceptions.Warning(
                    _('You have to select lines '
                      'from the same procurement location.'))
            else:
                location = line_location

    @api.model
    def default_get(self, fields):
        res = super(PurchaseRequestLineMakePurchaseOrder, self).default_get(
            fields)
        request_line_obj = self.env['purchase.request.line']
        request_line_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not request_line_ids:
            return res
        assert active_model == 'purchase.request.line', \
            'Bad context propagation'

        items = []
        self._check_valid_request_line(request_line_ids)
        for line in request_line_obj.browse(request_line_ids):
            items.append([0, 0, self._prepare_item(line)])
        res['item_ids'] = items
        return res

    @api.model
    def _prepare_purchase_order(self, picking_type, location, company):
        if not self.supplier_id:
            raise exceptions.Warning(
                _('Enter a supplier.'))
        supplier = self.supplier_id
        supplier_pricelist = supplier.property_product_pricelist  \
            or False
        data = {
            'origin': '',
            'partner_id': self.supplier_id.id,
            'pricelist_id': supplier_pricelist.id,
            'location_id': location.id,
            'fiscal_position': supplier.property_account_position_id and
            supplier.property_account_position_id.id or False,
            'picking_type_id': picking_type.id,
            'company_id': company.id,
            }
        return data

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        po_line_obj = self.env['purchase.order.line']
        product = item.product_id
        supplier = self.supplier_id
        pricelist_id = supplier.property_product_pricelist

        if pricelist_id:
            date_order_str = datetime.strptime(
                fields.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                DEFAULT_SERVER_DATETIME_FORMAT).\
                strftime(DEFAULT_SERVER_DATE_FORMAT)
            price = pricelist_id.price_get(prod_id=product.id,
                                           qty=item.product_qty or 1.0,
                                           partner=supplier or False,
                                           context={'uom':
                                                    product.uom_po_id.id,
                                                    'date': date_order_str})
            price = price[pricelist_id.id]
        else:
            price = product.standard_price

        vals = po_line_obj.onchange_product_id()
        vals.update({
            'name': product.name,
            'order_id': po.id,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'price_unit': price,
            'product_qty': item.product_qty,
            'account_analytic_id': item.line_id.analytic_account_id.id,
            'taxes_id': [(6, 0, vals.get('taxes_id', []))],
            'purchase_request_lines': [(4, item.line_id.id)],
            'date_planned':
                vals.get('date_planned', False) or item.line_id.date_required,

        })
        if item.line_id.procurement_id:
            vals['procurement_ids'] = [(4, item.line_id.procurement_id.id)]

        return vals

    @api.model
    def _get_order_line_search_domain(self, order, item):
        vals = self._prepare_purchase_order_line(order, item)
        order_line_data = [('order_id', '=', order.id),
                           ('product_id', '=', item.product_id.id or False),
                           ('product_uom', '=', vals['product_uom']),
                           ('account_analytic_id', '=',
                            item.line_id.analytic_account_id.id or False),
                           ]
        if not item.product_id:
            order_line_data.append(('name', '=', item.name))
        if not item.line_id.procurement_id and \
                item.line_id.procurement_id.location_id:
            order_line_data.append(
                ('location_id', '=',
                 item.line_id.procurement_id.location_id.id))
        return order_line_data

    @api.multi
    def make_purchase_order(self):
        res = []
        purchase_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line']
        pr_line_obj = self.env['purchase.request.line']
        purchase = False

        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise exceptions.Warning(
                    _('Enter a positive quantity.'))

            location = line.request_id.picking_type_id.default_location_dest_id
            if self.purchase_order_id:
                purchase = self.purchase_order_id
            if not purchase:
                po_data = self._prepare_purchase_order(
                    line.request_id.picking_type_id, location,
                    line.company_id)
                purchase = purchase_obj.create(po_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            if available_po_lines:
                po_line = available_po_lines[0]
                new_qty, new_price = pr_line_obj._calc_new_qty_price(
                    line, po_line=po_line)
                if new_qty > po_line.product_qty:
                    po_line.product_qty = new_qty
                    po_line.price_unit = new_price
                    po_line.purchase_request_lines = [(4, line.id)]
            else:
                po_line_data = self._prepare_purchase_order_line(purchase,
                                                                 item)
                po_line_obj.create(po_line_data)
            res.append(purchase.id)

        return {
            'domain': "[('id','in', ["+','.join(map(str, res))+"])]",
            'name': _('RFQ'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _name = "purchase.request.line.make.purchase.order.item"
    _description = "Purchase Request Line Make Purchase Order Item"

    wiz_id = fields.Many2one(
        'purchase.request.line.make.purchase.order',
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
    product_qty = fields.Float(string='Quantity to purchase',
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
