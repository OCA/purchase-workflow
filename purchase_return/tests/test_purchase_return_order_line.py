from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged, Form


@tagged('-at_install', 'post_install')
class TestPurchaseReturnOrderLine(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseReturnOrderLine, cls).setUpClass()
        uom_unit = cls.env.ref('uom.product_uom_unit')
        uom_hour = cls.env.ref('uom.product_uom_hour')
        cls.product_order = cls.env['product.product'].create({
            'name': "Zed+ Antivirus",
            'standard_price': 35.0,
            'list_price': 20.0,
            'type': 'consu',
            'uom_id': uom_unit.id,
            'uom_po_id': uom_unit.id,
            'purchase_method': 'purchase',
            'default_code': 'PROD_ORDER',
            'taxes_id': False,
        })
        cls.service_order = cls.env['product.product'].create({
            'name': "Prepaid Consulting",
            'standard_price': 40.0,
            'list_price': 90.0,
            'type': 'service',
            'uom_id': uom_hour.id,
            'uom_po_id': uom_hour.id,
            'purchase_method': 'purchase',
            'default_code': 'PRE-PAID',
            'taxes_id': False,
        })

    # Test to compute a price subtotal
    def test_compute_price_subtotal(self):
        # Create a Purchase Return Order
        purchase_return_order = self.env['purchase.return.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner_a.id,
        })
        PurchaseReturnOrderLine = self.env['purchase.return.order.line'].with_context(tracking_disable=True)
        po_line = PurchaseReturnOrderLine.create({
            'name': self.product_order.name,
            'product_id': self.product_order.id,
            'product_qty': 10.0,
            'product_uom': self.product_order.uom_id.id,
            'price_unit': self.product_order.list_price,
            'order_id': purchase_return_order.id,
            'refund_only': True,
            'taxes_id': False,
        })
        price_subtotal = po_line.product_qty * self.product_order.list_price
        po_line._compute_amount()
        self.assertEqual(po_line.price_subtotal, price_subtotal)
        po_line.product_qty = 4.0
        price_subtotal = po_line.product_qty * self.product_order.list_price
        self.assertEqual(po_line.price_subtotal, price_subtotal)

    # Test to suggest a minimal quantity based on the seller
    def test_suggest_quantity(self):
        # Create a Purchase Return Order
        purchase_return_order = self.env['purchase.return.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner_a.id,
        })
        # Create a Purchase Return Order Line
        PurchaseReturnOrderLine = self.env['purchase.return.order.line'].with_context(tracking_disable=True)
        po_line = PurchaseReturnOrderLine.create({
            'name': self.product_order.name,
            'product_id': self.product_order.id,
            'product_qty': 10.0,
            'product_uom': self.product_order.uom_id.id,
            'price_unit': self.product_order.list_price,
            'order_id': purchase_return_order.id,
            'refund_only': True,
            'taxes_id': False,
        })
        vendor = po_line.product_id.seller_ids.create({
            'name': self.partner_a.id,
            'min_qty': 50.0,
        })
        self.product_order.seller_ids = vendor
        po_line._suggest_quantity()
        self.assertEqual(po_line.product_qty, vendor.min_qty)

    # Test to update all columns of a Purchase Return Order Line on change product
    def test_onchange_product_id(self):
        # Create a Purchase Return Order
        purchase_return_order = self.env['purchase.return.order'].with_context(tracking_disable=True).create({
            'partner_id': self.partner_a.id,
        })
        # Create a Purchase Return Order Line
        PurchaseReturnOrderLine = self.env['purchase.return.order.line'].with_context(tracking_disable=True)
        po_line = PurchaseReturnOrderLine.create({
            'name': self.product_order.name,
            'product_id': self.product_order.id,
            'product_qty': 10.0,
            'product_uom': self.product_order.uom_id.id,
            'price_unit': self.product_order.list_price,
            'order_id': purchase_return_order.id,
            'refund_only': True,
            'taxes_id': False,
        })
        vendor = po_line.product_id.seller_ids.create({
            'name': self.partner_a.id,
            'min_qty': 50.0,
        })
        self.service_order.seller_ids = vendor
        po_line.product_id = self.service_order
        po_line.onchange_product_id()
        self.assertEqual(po_line.product_id, self.service_order)
        self.assertEqual(po_line.product_qty, vendor.min_qty)
        self.assertEqual(po_line.product_uom, self.service_order.uom_id)
        self.assertEqual(po_line.order_id, purchase_return_order)

