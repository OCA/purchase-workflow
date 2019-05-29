# Copyright 2015-2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta
import odoo.tests.common as common
from odoo import fields


class TestProcurementOrder(common.TransactionCase):

    def setUp(self):
        """ Create a packagings with uom  product_uom_dozen on
                * product_product_3 (uom is product_uom_unit)
        """
        super(TestProcurementOrder, self).setUp()
        self.procurement_group_obj = self.env['procurement.group']
        self.stock_move_obj = self.env['stock.move']
        self.po_line_obj = self.env['purchase.order.line']
        self.unit = self.env.ref('uom.product_uom_unit')
        self.unit_dozen = self.env.ref('uom.product_uom_dozen')
        self.route_buy = self.env.ref("purchase_stock.route_warehouse0_buy")
        product_obj = self.env['product.product']
        # Create new product
        vals = {
            'name': 'Product Purchase Pack Test',
            'categ_id': self.env.ref('product.product_category_5').id,
            'list_price': 30.0,
            'standard_price': 20.0,
            'type': 'product',
            'uom_id': self.unit.id,

        }
        self.product_test = product_obj.create(vals)
        self.product_packaging_3 = self.env['product.packaging'].create({
            'product_id': self.product_test.id,
            'uom_id': self.env.ref('uom.product_uom_dozen').id,
            'name': 'Packaging Dozen'
        })
        self.sp_30 = self.env.ref('product.product_supplierinfo_1')
        self.sp_30.product_tmpl_id = self.product_packaging_3.\
            product_id.product_tmpl_id
        self.sp_30.currency_id = self.env.user.company_id.currency_id
        date_m_10 = fields.Datetime.now() - timedelta(days=10)

        self.sp_30.date_start = fields.Datetime.to_string(date_m_10)
        self.product_uom_8 = self.env['uom.uom'].create({
            'category_id': self.env.ref('uom.product_uom_categ_unit').id,
            'name': 'COL8',
            'factor_inv': 8,
            'uom_type': 'bigger',
            'rounding': 1.0,
        })
        self.env['purchase.order'].search([
            ("state", "=", "draft")
        ]).button_cancel()
        self.procurement_group = self.procurement_group_obj.create({
            'name': 'TEST'
        })

    def test_stock_rule(self):
        # On supplierinfo set price to 3
        # On supplierinfo set min_qty as 0
        # Create procurement line with rule buy and quantity 17
        # run stock rule
        self.product_test.route_ids = [(
            4, self.route_buy.id)]
        self.unit.rounding = 1

        self.sp_30.min_qty = 0
        self.sp_30.price = 3

        self.procurement_group_obj.run(
            self.product_test,
            17,
            self.unit,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )
        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 17
        # Check product_qty is 17
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
        ])

        self.assertEqual(
            self.unit,
            line.product_purchase_uom_id)
        self.assertEqual(
            17,
            line.product_purchase_qty)
        self.assertEqual(
            17,
            line.product_qty)
        self.assertFalse(line.packaging_id)
        self.assertEqual(
            self.unit,
            line.product_uom)
        self.assertEqual(
            3,
            line.price_unit)
        #  Confirm Purchase Order to avoid group
        line.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        self.procurement_group_obj.run(
            self.product_test,
            1,
            self.unit_dozen,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )
        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 12
        # Check product_qty is 12
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(
            self.unit,
            line.product_purchase_uom_id)
        self.assertEqual(
            12,
            line.product_purchase_qty)
        self.assertEqual(
            12,
            line.product_qty)
        self.assertFalse(line.packaging_id)
        self.assertEqual(
            self.unit,
            line.product_uom)
        self.assertEqual(
            3,
            line.price_unit)
        # Confirm Purchase Order to avoid group
        line.order_id.button_confirm()

        # On supplierinfo set product_uom_8 as min_qty_uom_id
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.min_qty_uom_id = self.product_uom_8
        self.procurement_group_obj.run(
            self.product_test,
            17,
            self.unit,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )
        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 3
        # Check product_qty is 8*3 = 24
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(
            self.product_uom_8,
            line.product_purchase_uom_id)
        self.assertEqual(
            3,
            line.product_purchase_qty)
        self.assertEqual(
            24,
            line.product_qty)
        self.assertFalse(line.packaging_id)
        self.assertEqual(
            self.unit,
            line.product_uom)
        self.assertEqual(
            3,
            line.price_unit)
        # Confirm Purchase Order to avoid group
        line.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        self.procurement_group_obj.run(
            self.product_test,
            1,
            self.unit_dozen,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )

        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 2
        # Check product_qty is 8*2 = 16
        # Check packaging_id is False
        # Check product_uom is product_uom_unit
        # Check price_unit is 3
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(
            self.product_uom_8,
            line.product_purchase_uom_id)
        self.assertEqual(
            2,
            line.product_purchase_qty)
        self.assertEqual(
            16,
            line.product_qty)
        self.assertFalse(line.packaging_id)
        self.assertEqual(
            self.unit,
            line.product_uom)
        self.assertEqual(
            3,
            line.price_unit)
        # Confirm Purchase Order to avoid group
        line.order_id.button_confirm()

        # On supplierinfo set packaging product_packaging_3 (dozen)
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.packaging_id = self.product_packaging_3
        self.procurement_group_obj.run(
            self.product_test,
            17,
            self.unit,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )

        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 1
        # Check product_qty is 8*1 = 8
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        # Check price_unit is 3*12 = 36
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(
            self.product_uom_8,
            line.product_purchase_uom_id)
        self.assertEqual(
            1,
            line.product_purchase_qty)
        self.assertEqual(
            8,
            line.product_qty)
        self.assertEqual(
            self.product_packaging_3,
            line.packaging_id)
        self.assertEqual(
            self.unit_dozen,
            line.product_uom)
        self.assertEqual(
            3,
            line.price_unit)
        # Confirm Purchase Order to avoid group
        line.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # run procurement
        self.procurement_group_obj.run(
            self.product_test,
            1,
            self.unit_dozen,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )

        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_8
        # Check product_purchase_qty is 1
        # Check product_qty is 8*1 = 8
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(
            self.product_uom_8,
            line.product_purchase_uom_id)
        self.assertEqual(
            1,
            line.product_purchase_qty)
        self.assertEqual(
            8,
            line.product_qty)
        self.assertEqual(
            self.product_packaging_3,
            line.packaging_id)
        self.assertEqual(
            self.unit_dozen,
            line.product_uom)
        self.assertEqual(
            3,
            line.price_unit)
        # Confirm Purchase Order to avoid group
        line.order_id.button_confirm()

        # On supplierinfo set product_uom_unit as min_qty_uom_id
        # Create procurement line with rule buy and quantity 17
        # run procurement
        self.sp_30.min_qty_uom_id = self.unit

        self.procurement_group_obj.run(
            self.product_test,
            17,
            self.unit,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )
        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 2
        # Check product_qty is 2
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(
            self.unit,
            line.product_purchase_uom_id)
        self.assertEqual(
            2,
            line.product_purchase_qty)
        self.assertEqual(
            2,
            line.product_qty)
        self.assertEqual(
            self.product_packaging_3,
            line.packaging_id)
        self.assertEqual(
            self.unit_dozen,
            line.product_uom)
        self.assertEqual(
            3,
            line.price_unit)
        # Confirm Purchase Order to avoid group
        line.order_id.button_confirm()

        # Create procurement line with rule buy and quantity 1 dozen
        # set purcahse price to 36
        # run procurement
        self.sp_30.price = 36
        self.procurement_group_obj.run(
            self.product_test,
            1,
            self.unit_dozen,
            self.env.ref('stock.stock_location_stock'),
            'TEST',
            'TEST',
            {
                'group_id': self.procurement_group.id,
            },
        )

        self.procurement_group_obj.run_scheduler()
        # Check product_purchase_uom_id is product_uom_unit
        # Check product_purchase_qty is 1
        # Check product_qty is 1
        # Check packaging_id is product_packaging_3
        # Check product_uom is product_uom_dozen
        # Check price_unit is 3*12 = 36
        line = self.po_line_obj.search([
            ('product_id', '=', self.product_test.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(
            self.unit,
            line.product_purchase_uom_id)
        self.assertEqual(
            1,
            line.product_purchase_qty)
        self.assertEqual(
            1,
            line.product_qty)
        self.assertEqual(
            self.product_packaging_3,
            line.packaging_id)
        self.assertEqual(
            self.unit_dozen,
            line.product_uom)
        self.assertEqual(
            36,
            line.price_unit)
        line.order_id.button_confirm()

    def test_procurement_from_orderpoint_draft_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Change the stock minimum to 11 PC
        # The purchase quantity should remains 12
        # Change the stock minimum to 13 PC
        # The purchase quantity should increase up to 24
        warehouse = self.env.ref('stock.warehouse0')
        product = self.product_test
        product.route_ids = [(
            4, self.route_buy.id)]
        self.unit_dozen.rounding = 1

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.unit_dozen

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        self.procurement_group_obj.run_scheduler()
        lines = self.po_line_obj.search([
            ('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(lines)
        self.assertEqual(len(lines), 1)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([
            ('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(lines)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 24)

    def test_procurement_from_orderpoint_sent_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Send the purchase order
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref('stock.warehouse0')
        product = self.product_test
        product.route_ids = [(
            4, self.route_buy.id)]
        self.unit_dozen.rounding = 1

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.unit_dozen

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 12)

        line.order_id.write({'state': 'sent'})

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        self.procurement_group_obj.run_scheduler()
        lines = self.po_line_obj.search([
            ('orderpoint_id', '=', orderpoint.id)])

        self.assertEqual(len(lines), 2)

        for line in lines:
            self.assertEqual(line.product_qty, 12)

    def test_procurement_from_orderpoint_to_approve_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Set the purchase order to approve
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref('stock.warehouse0')
        product = self.product_test
        product.route_ids = [(
            4, self.route_buy.id)]
        self.unit_dozen.rounding = 1

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.unit_dozen

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 12)

        line.order_id.write({'state': 'to approve'})

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(line)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        self.procurement_group_obj.run_scheduler()
        lines = self.po_line_obj.search([
            ('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(lines), 2)
        for line in lines:
            self.assertEqual(line.product_qty, 12)

    def test_procurement_from_orderpoint_confirmed_po(self):
        # Define a multiple of 12 on supplier info
        # Trigger a stock minimum rule of 10 PC
        # A purchase line with 12 PC should be generated
        # Confirm the purchase order
        # Change the stock minimum to 11 PC
        # No new purchase should be generated
        # Change the stock minimum to 13 PC
        # A new purchase should be generated
        warehouse = self.env.ref('stock.warehouse0')
        product = self.product_test
        product.route_ids = [(
            4, self.route_buy.id)]
        self.unit_dozen.rounding = 1

        self.sp_30.min_qty = 1
        self.sp_30.min_qty_uom_id = self.unit_dozen

        orderpoint = self.env['stock.warehouse.orderpoint'].create({
            'warehouse_id': warehouse.id,
            'location_id': warehouse.lot_stock_id.id,
            'product_id': product.id,
            'product_min_qty': 10,
            'product_max_qty': 10,
        })
        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([('orderpoint_id', '=', orderpoint.id)])
        self.assertEqual(len(line), 1)

        self.assertEqual(line.product_qty, 12)

        line.order_id.button_confirm()

        # change order_point level and rerun
        orderpoint.product_min_qty = 11
        orderpoint.product_max_qty = 11

        self.procurement_group_obj.run_scheduler()
        line = self.po_line_obj.search([
            ('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(line)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_qty, 12)

        # change order_point level and rerun
        orderpoint.product_min_qty = 13
        orderpoint.product_max_qty = 13

        self.procurement_group_obj.run_scheduler()
        lines = self.po_line_obj.search([
            ('orderpoint_id', '=', orderpoint.id)])

        self.assertTrue(lines)
        self.assertEqual(len(lines), 2)
