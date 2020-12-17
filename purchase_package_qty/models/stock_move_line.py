from openerp import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    package_qty = fields.Float(
        'Package Qty',
        help="""The quantity of products in the supplier package.""")
    product_qty_package = fields.Float(
        'Number of packages', help="""The number of packages you'll buy.""",)
#     qty_done = fields.Float("Done (uom)")
    qty_done_package = fields.Float(
        "Done (package)", help="""The number of packages you've received.""")

    @api.onchange('qty_done')
    def onchange_qty_done(self):
        if self.package_qty:
            self.qty_done_package = self.qty_done / self.package_qty

    @api.onchange('qty_done_package')
    def onchange_qty_done_package(self):
        if self.qty_done_package == int(self.qty_done_package):
            self.qty_done = self.package_qty * self.qty_done_package

    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        res = super(StockMoveLine, self).onchange_product_id()
        if self.product_id and self.picking_id:
            supplier = self.product_id._select_seller(
                partner_id=self.picking_id.partner_id, quantity=1)
            if supplier:
                if not res.get('value', False):
                    res['value'] = {}
                res['value']['package_qty'] = supplier.package_qty
        return res

    @api.onchange('product_qty_package')
    def product_qty_package_onchange(self):
        if self.product_qty_package == int(self.product_qty_package):
            self.product_qty = self.product_qty_package * self.package_qty
