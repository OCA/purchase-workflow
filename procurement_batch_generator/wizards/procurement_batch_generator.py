# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class ProcurementBatchGenerator(models.TransientModel):
    _name = 'procurement.batch.generator'
    _description = 'Wizard to create procurements from product tree'

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        for line in self.line_ids:
            line.warehouse_id = self.warehouse_id.id
    
    @api.onchange('date')
    def onchange_date(self):
        for line in self.line_ids:
            line.date_planned = self.date
    
    @api.onchange('default_quantity')
    def onchange_default_quantity(self):
        _logger.debug("ONCHANGE defaul qty")
        for line in self.line_ids:
            line.procurement_qty = self.default_quantity
    
    @api.model
    def _default_lines(self):
        assert isinstance(self.env.context['active_ids'], list),\
            "context['active_ids'] must be a list"
        assert self.env.context['active_model'] == 'product.product',\
            "context['active_model'] must be 'product.product'"
        res = []
 
        warehouse_id  = self._get_default_warehouse()

        today = fields.Date.context_today(self)
        for product in self.env['product.product'].browse(
                self.env.context['active_ids']):
            res.append({
                'product_id': product.id,
                'qty_available': product.qty_available,
                'outgoing_qty': product.outgoing_qty,
                'incoming_qty': product.incoming_qty,
                'uom_id': product.uom_id.id,
                'procurement_qty': 0.0,
                'warehouse_id': warehouse_id,
                'date_planned': today,
                })
        return res

    @api.model
    def _get_default_warehouse(self):
        warehouses = self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.user.company_id.id)])
        warehouse_id = warehouses and warehouses[0].id or False
        return warehouse_id

    line_ids = fields.One2many(
        'procurement.batch.generator.line', 'parent_id',
        string='Procurement Request Lines', default=_default_lines)    
    date = fields.Date(string="Procurement Date", 
        default=lambda self:fields.Date.context_today(self))
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", 
        string="Warehouse", default=_get_default_warehouse, required=1)
    comment = fields.Text(string="Comment")
    default_quantity = fields.Float(string="Default Quantity", default=1.0)
    route_ids = fields.Many2many('stock.location.route', string='Preferred Routes')
    
    @api.multi
    def validate(self):
        self.ensure_one()
        wiz = self[0]
        assert wiz.line_ids, 'wizard must have some lines'
        new_po_ids = []
        for line in wiz.line_ids:
            if not line.procurement_qty:
                continue
            procurement = self.env['procurement.order'].create(
                line._prepare_procurement_order())
            new_po_ids.append(procurement.id)
        if not new_po_ids:
            raise Warning(_('All requested quantities are null.'))
        self.pool['procurement.order'].signal_workflow(
            self._cr, self._uid, new_po_ids, 'button_confirm')
        self.pool['procurement.order'].run(
            self._cr, self._uid, new_po_ids, context=self.env.context)
        action = self.env['ir.actions.act_window'].for_xml_id(
            'procurement', 'procurement_action')
        action['domain'] = [('id', 'in', new_po_ids)]
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
    

    @api.multi
    def _prepare_procurement_order(self):
        self.ensure_one()
        comment = self.env.user.login 
        if self.parent_id.comment :
            comment += '\n'+ self.parent_id.comment
        vals = {
            'name': u'INT: ' + unicode(comment),
            'origin':u'INT: ' + unicode(self.env.user.login ),
            'product_id': self.product_id.id,
            'product_qty': self.procurement_qty,
            'product_uom': self.uom_id.id,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'company_id': self.warehouse_id.company_id.id,
            'date_planned': self.date_planned,
            'warehouse_id': self.warehouse_id.id,
            
            }
        if self.parent_id.route_ids:
            vals.update({
                'route_ids': [(6, 0, 
                    [r.id for r in self.parent_id.route_ids])],
            })
        return vals
