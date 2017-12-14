# -*- coding: utf-8 -*-
# © 2014-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.tools import float_is_zero
from odoo.exceptions import UserError


class ProcurementBatchGenerator(models.TransientModel):
    _name = 'procurement.batch.generator'
    _description = 'Wizard to create procurements from product tree'

    @api.model
    def _default_lines(self):
        assert isinstance(self.env.context['active_ids'], list),\
            "context['active_ids'] must be a list"
        assert self.env.context['active_model'] == 'product.product',\
            "context['active_model'] must be 'product.product'"
        res = []
        warehouses = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.user.company_id.id)])
        warehouse_id = warehouses and warehouses[0].id or False
        today = fields.Date.context_today(self)
        for product in self.env['product.product'].browse(
                self.env.context['active_ids']):
            part_id = product.seller_ids and product.seller_ids[0].id or False
            res.append({
                'product_id': product.id,
                'partner_id': part_id,
                'qty_available': product.qty_available,
                'outgoing_qty': product.outgoing_qty,
                'incoming_qty': product.incoming_qty,
                'uom_id': product.uom_id.id,
                'procurement_qty': 0.0,
                'warehouse_id': warehouse_id,
                'date_planned': today,
                })
        return res

    line_ids = fields.One2many(
        'procurement.batch.generator.line', 'parent_id',
        string='Procurement Request Lines', default=_default_lines)

    @api.multi
    def validate(self):
        self.ensure_one()
        wiz = self[0]
        if not wiz.line_ids:
            raise UserError(_('There are no lines!'))
        poo = self.env['procurement.order']
        procs = poo
        prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for line in wiz.line_ids:
            if float_is_zero(line.procurement_qty, precision_digits=prec):
                continue
            proc = poo.create(line._prepare_procurement_order())
            procs += proc
        if not procs:
            raise UserError(_('All requested quantities are null.'))
        # No need to run() the procurements ?
        action = self.env['ir.actions.act_window'].for_xml_id(
            'procurement', 'procurement_action')
        action['domain'] = [('id', 'in', procs.ids)]
        return action


class ProcurementBatchGeneratorLine(models.TransientModel):
    _name = 'procurement.batch.generator.line'
    _description = 'Lines of the wizard to request procurements'

    parent_id = fields.Many2one(
        'procurement.batch.generator', string='Parent')
    product_id = fields.Many2one(
        'product.product', string='Product', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Supplier')
    qty_available = fields.Float(
        string='Quantity Available',
        digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    outgoing_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    incoming_qty = fields.Float(
        string='Incoming Quantity',
        digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    procurement_qty = fields.Float(
        string='Requested Quantity',
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    uom_id = fields.Many2one(
        'product.uom', string='Unit of Measure', readonly=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', required=True)
    date_planned = fields.Date(string='Planned Date', required=True)
    route_ids = fields.Many2many(
        'stock.location.route', string='Preferred Routes')

    @api.multi
    def _prepare_procurement_order(self):
        self.ensure_one()
        vals = {
            'name': u'INT: %s' % self.env.user.login,
            'date_planned': self.date_planned,
            'product_id': self.product_id.id,
            'product_qty': self.procurement_qty,
            'product_uom': self.uom_id.id,
            'warehouse_id': self.warehouse_id.id,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'company_id': self.warehouse_id.company_id.id,
            'route_ids': [(6, 0, self.route_ids.ids)],
            }
        return vals
