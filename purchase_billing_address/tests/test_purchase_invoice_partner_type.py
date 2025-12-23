# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPurchaseInvoicePartnerType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        ResPartner = cls.env["res.partner"]
        PurchaseOrder = cls.env["purchase.order"]
        cls.partner_id = ResPartner.create(
            {"name": "Supplier parent", "type": "purchase_invoice", "supplier_rank": 1}
        )
        cls.supplier_id = ResPartner.create(
            {
                "name": "Supplier",
                "type": "purchase_invoice",
                "supplier_rank": 1,
                "parent_id": cls.partner_id.id,
            }
        )
        cls.product_id = cls.env.ref("product.product_product_5")
        cls.product_id.write({"purchase_method": "purchase"})
        cls.purchase_order_id = PurchaseOrder.create(
            {
                "partner_id": cls.partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_id.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        }
                    )
                ],
            }
        )

    def test_address_purchase_invoice_get(self):
        partner_ids = self.purchase_order_id._address_purchase_invoice_get()
        self.assertEqual(partner_ids, [self.supplier_id.id])

    def test_compute_available_partner_invoice_ids(self):
        self.purchase_order_id._compute_available_partner_invoice_ids()
        self.assertEqual(
            self.purchase_order_id.available_partner_invoice_ids.ids,
            [self.supplier_id.id],
        )

    def test_onchange_partner_id(self):
        self.purchase_order_id.onchange_partner_id()
        self.assertEqual(self.purchase_order_id.partner_invoice_id, self.supplier_id)

    def test_create_invoice(self):
        self.purchase_order_id.onchange_partner_id()
        self.purchase_order_id.button_confirm()
        self.purchase_order_id.action_create_invoice()
        invoice = self.purchase_order_id.invoice_ids[0]
        self.assertEqual(invoice.partner_id, self.supplier_id)
