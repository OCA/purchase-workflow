# Copyright 2019 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPurchaseSaleLink(TransactionCase):

    def setUp(self):
        """Create a Sale Order with :
            - 2 service products purchased automatically
            - 1 stockable product with a two-step MTO route
        Each product has his own vendor/supplier, to easily check the number of
        expected linked Purchase Orders.
        """
        super(TestPurchaseSaleLink, self).setUp()

        self.vendors = self.env['res.partner'].create([
            {'name': 'vendor_0', 'supplier': True},
            {'name': 'vendor_1', 'supplier': True},
            {'name': 'vendor_2', 'supplier': True},
        ])

        self.customer = self.env.ref('base.res_partner_2')

        # Set the warehouse's Incoming Shipments in two_steps mode
        # to check if the module works even if the link between the SO and
        # the Purchase Oder lines is not direct.
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse.reception_steps = 'two_steps'

        route_buy = self.env.ref('purchase_stock.route_warehouse0_buy').id
        route_mto = self.env.ref('stock.route_warehouse0_mto').id

        self.products = self.env["product.product"].create([
            {
                'name': 'product_service_0',
                'type': 'service',
                'categ_id': 1,
                'service_to_purchase': True,
                'seller_ids': [(0, 0, {'name': self.vendors[0].id})],
            },
            {
                'name': 'product_service_1',
                'type': 'service',
                'categ_id': 1,
                'service_to_purchase': True,
                'seller_ids': [(0, 0, {'name': self.vendors[1].id})],
            },
            {
                'name': 'product_stock_0',
                'type': 'product',
                'categ_id': 1,
                'route_ids': [(6, 0, [route_buy, route_mto])],
                'seller_ids': [(0, 0, {'name': self.vendors[2].id})],
            }
        ])

        self.vendors_names = self.vendors.mapped('name')
        self.products_names = self.products.mapped('name')

        # Creating Sale Order
        self.so = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'warehouse_id': self.warehouse.id,
        })
        self.sol0 = self.env['sale.order.line'].create({
            'name': self.products[0].name,
            'product_id': self.products[0].id,
            'product_uom_qty': 1,
            'order_id': self.so.id,
        })
        self.sol1 = self.env['sale.order.line'].create({
            'name': self.products[1].name,
            'product_id': self.products[1].id,
            'product_uom_qty': 1,
            'order_id': self.so.id,
        })
        self.sol2 = self.env['sale.order.line'].create({
            'name': self.products[2].name,
            'product_id': self.products[2].id,
            'product_uom_qty': 1,
            'order_id': self.so.id,
        })

        self.so.action_confirm()

        # Acces the Purchase Orders from the Sale Order
        action = self.so.action_view_purchase()
        self.purchase_orders = self.env['purchase.order']\
            .search(action['domain'])

    def test_sale_purchase_link(self):
        # Check if the good number of Purchase Orders was created
        self.assertEqual(
            self.so.purchase_order_count,
            len(self.vendors_names),
            "%s Purchase Oders expected, only %s were created" %
            (len(self.vendors_names), len(self.purchase_orders))
        )

        self.assertEqual(len(self.purchase_orders), len(self.vendors_names))

        # Check if the purchase orders created have the expected
        # supplier and product
        for po in self.purchase_orders:
            self.assertTrue(po.partner_id.name in self.vendors_names)
            self.assertTrue(po.product_id.name in self.products_names)

    def test_purchase_sale_link(self):
        for po in self.purchase_orders:
            action = po.action_view_sale_order()
            so = self.env['sale.order'].search([('id', '=', action['res_id'])])

            # Check if the Sale Order related to each Purchase Order
            # is the Sale Order we've created
            self.assertEqual(so.id, self.so.id)
            self.assertEqual(po.sale_order_count, 1)
