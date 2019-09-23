# Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tests import Form


class TestPurchaseComputeOrder(TransactionCase):

    def setUp(self):
        super(TestPurchaseComputeOrder, self).setUp()
        self.partner_3 = self.env.ref('base.res_partner_3')
        self.cmp_purchase_order = self.env['computed.purchase.order'].create(
            {'partner_id': self.partner_3.id,
             'purchase_target': 20,
             'target_type': 'time',
             # 'compute_pending_quantity': False
             })
        self.product = self.env.ref('product.product_delivery_01')
        self.product.consumption_calculation_method = 'moves'
        self.product.calculation_range = 10
        self.picking_type = self.env.ref('stock.picking_type_out')
        picking_form = Form(self.env['stock.picking'])
        picking_form.partner_id = self.partner_3
        picking_form.picking_type_id = self.picking_type
        self.picking = picking_form.save()
        self.picking.onchange_picking_type()
        self.move = self.env['stock.move'].create({
            'picking_id': self.picking.id,
            'product_id': self.product.id,
            'name': 'Test',
            'product_uom_qty': 20,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'quantity_done': 20,
            'location_id': self.picking.location_id.id,
            'location_dest_id': self.picking.location_dest_id.id,
        })
        self.picking.button_validate()
        self.cmp_purchase_order.compute_active_product_stock()
        self.cmp_po_line = self.cmp_purchase_order.line_ids.filtered(
            lambda l: l.product_id.id == self.product.id)

    def test_001_get_product_and_stock(self):
        self.cmp_po_line.average_consumption = 15
        self.assertEquals(self.cmp_po_line.qty_available, 80.0,
                          "Available Quantity of a product should be 80.0")

    def test_002_compute_purchase_quantities(self):
        self.cmp_po_line.average_consumption = 15
        self.cmp_purchase_order.compute_purchase_quantities()
        self.assertEquals(self.cmp_po_line.purchase_qty, 60.0,
                          "Purchase Quantity of a product should be 60.0")

    def test_003_make_purchase_order(self):
        self.cmp_po_line.average_consumption = 15
        self.cmp_purchase_order.compute_purchase_quantities()
        self.cmp_purchase_order.make_order()
        po_line = self.cmp_purchase_order.purchase_order_id.order_line\
            .filtered(lambda l: l.product_id.id == self.product.id)
        self.assertEquals(po_line.product_qty, self.cmp_po_line.purchase_qty,
                          "Purchase Quantity of a product should be "
                          "%s" % self.cmp_po_line.purchase_qty)
