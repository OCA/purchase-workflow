# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.fields import Command
from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRequisitionStockDropshipping(BaseCommon):
    def test_purchase_requisition_stock_dropshipping(self):
        # create 'dropship - call for tender' product
        product = self.env["product.product"].create({"name": "prsds-product"})
        dropshipping_route = self.env.ref("stock_dropshipping.route_drop_shipping")
        product.write({"route_ids": [Command.set([dropshipping_route.id])]})
        product.write({"purchase_requisition": "tenders"})
        requisition_type = self.env["purchase.requisition.type"].create(
            {"name": "Call for Tender", "quantity_copy": "copy"}
        )

        # sell this product
        customer = self.env["res.partner"].create({"name": "prsds-customer"})
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "partner_invoice_id": customer.id,
                "partner_shipping_id": customer.id,
                "order_line": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 10.00,
                            "product_uom": product.uom_id.id,
                            "price_unit": 10,
                        }
                    )
                ],
            }
        )

        # confirm order
        sale_order.action_confirm()

        # call for tender must exists
        call_for_tender = self.env["purchase.requisition"].search(
            [("origin", "=", sale_order.name)]
        )
        self.assertTrue(call_for_tender)
        call_for_tender.type_id = requisition_type

        # confirm call for tender
        call_for_tender.action_in_progress()

        # create purchase order from call for tender
        vendor = self.env["res.partner"].create({"name": "prsds-vendor"})
        call_for_tender.vendor_id = vendor
        f = Form(
            self.env["purchase.order"].with_context(
                default_requisition_id=call_for_tender
            )
        )
        purchase_order = f.save()

        # check purchase order
        self.assertEqual(
            purchase_order.requisition_id.id,
            call_for_tender.id,
            "Purchase order should be linked with call for tender",
        )
        self.assertEqual(
            purchase_order.dest_address_id.id,
            customer.id,
            "Purchase order should be delivered at customer",
        )
        self.assertEqual(
            len(purchase_order.order_line), 1, "Purchase order should have one line"
        )
        purchase_order_line = purchase_order.order_line
        self.assertEqual(
            purchase_order_line.sale_order_id.id,
            sale_order.id,
            "Purchase order should be linked with sale order",
        )
        self.assertEqual(
            purchase_order_line.sale_line_id.id,
            sale_order.order_line.id,
            "Purchase order line should be linked with sale order line",
        )
        purchase_order.button_confirm()
        self.assertEqual(
            len(purchase_order.picking_ids),
            1,
            "Purchase order picking should be created",
        )
        self.assertEqual(
            purchase_order.picking_ids,
            sale_order.picking_ids,
            "Purchase order picking should be linked with sale order picking",
        )
