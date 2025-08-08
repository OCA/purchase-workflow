# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseRequisitionStockDropshipping(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        dropshipping_route = cls.env.ref("stock_dropshipping.route_drop_shipping")
        # add the group to the user to display the picking type in the form view
        # and its is saved in the purchase order
        cls.env.user.groups_id += cls.env.ref("stock.group_stock_multi_locations")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "purchase_requisition": "tenders",
                "route_ids": [Command.set([dropshipping_route.id])],
            }
        )
        cls.vendor = cls.env["res.partner"].create({"name": "vendor"})
        cls.customer = cls.env["res.partner"].create({"name": "customer"})
        cls.requisition_type = cls.env["purchase.requisition.type"].create(
            {"name": "Call for Tender", "quantity_copy": "copy"}
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "partner_invoice_id": cls.customer.id,
                "partner_shipping_id": cls.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 10.00,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 10,
                        }
                    )
                ],
            }
        )

    def test_purchase_requisition_dropshipping(self):
        self.sale_order.action_confirm()
        purchase_requisition = self.env["purchase.requisition"].search(
            [("origin", "=", self.sale_order.name)]
        )
        self.assertTrue(purchase_requisition)
        purchase_requisition.type_id = self.requisition_type
        # confirm call for tender
        purchase_requisition.vendor_id = self.vendor
        self.assertEqual(purchase_requisition.picking_type_id.code, "dropship")
        purchase_requisition.action_in_progress()
        purchase_form = Form(
            self.env["purchase.order"].with_context(
                default_requisition_id=purchase_requisition
            )
        )
        purchase_order = purchase_form.save()
        # check purchase order
        self.assertEqual(purchase_order.requisition_id.id, purchase_requisition.id)
        self.assertEqual(purchase_order.picking_type_id.code, "dropship")
        self.assertEqual(purchase_order.dest_address_id.id, self.customer.id)
        self.assertEqual(len(purchase_order.order_line), 1)
        self.assertEqual(purchase_order.order_line.sale_order_id.id, self.sale_order.id)
        self.assertEqual(
            purchase_order.order_line.sale_line_id.id, self.sale_order.order_line.id
        )
        purchase_order.button_confirm()
        self.assertEqual(len(purchase_order.picking_ids), 1)
        self.assertEqual(purchase_order.picking_ids, self.sale_order.picking_ids)
