# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import SavepointCase


class TestAccountFiscalPositionAllowedJournalPurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountFiscalPositionAllowedJournalPurchase, cls).setUpClass()

        # MODELS
        cls.account_model = cls.env["account.account"]
        cls.account_move_model = cls.env["account.move"]
        cls.fiscal_position_model = cls.env["account.fiscal.position"]
        cls.journal_model = cls.env["account.journal"]
        cls.partner_model = cls.env["res.partner"]
        cls.product_product_model = cls.env["product.product"]
        cls.purchase_order_model = cls.env["purchase.order"]

        # INSTANCES
        cls.fiscal_position_01 = cls.fiscal_position_model.create(
            {"name": "Fiscal position 01"}
        )
        cls.journal_01 = cls.journal_model.search([("type", "=", "purchase")], limit=1)
        cls.journal_02 = cls.journal_01.copy()
        cls.partner_01 = cls.partner_model.search([], limit=1)
        cls.product_01 = cls.product_product_model.search(
            [("type", "=", "service")], limit=1
        )
        cls.purchase_order_01 = cls.purchase_order_model.create(
            {
                "partner_id": cls.partner_01.id,
                "fiscal_position_id": cls.fiscal_position_01.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Purchase order line 01",
                            "product_id": cls.product_01.id,
                            "product_uom": cls.product_01.uom_id.id,
                            "product_qty": 1,
                            "price_unit": 1,
                            "date_planned": fields.Date.today(),
                        },
                    )
                ],
            }
        )
        cls.purchase_order_01.button_confirm()
        cls.invoice_01 = cls.account_move_model.create(
            {
                "type": "in_invoice",
                "partner_id": cls.partner_01.id,
                "journal_id": cls.journal_01.id,
                "fiscal_position_id": cls.fiscal_position_01.id,
            }
        )

    def test_01(self):
        """
        Data:
            - A draft invoice
            - A confirmed purchase order with a fiscal position
            - Exactly one purchase journal allowed on the fiscal position
        Test case:
            - Set the purchase order on the invoice
        Expected result:
            - The allowed purchase journal is set on the invoice
        """
        self.fiscal_position_01.allowed_journal_ids = [(6, 0, self.journal_02.ids)]
        self.invoice_01.purchase_id = self.purchase_order_01
        self.invoice_01._onchange_purchase_auto_complete()
        self.assertEqual(self.invoice_01.journal_id, self.journal_02)

    def test_02(self):
        """
        Data:
            - A draft invoice
            - A confirmed purchase order with no fiscal position
        Test case:
            - Set the purchase order on the invoice
        Expected result:
            - The journal of the invoice didn't change
        """
        self.purchase_order_01.fiscal_position_id = False
        self.invoice_01.purchase_id = self.purchase_order_01
        self.invoice_01._onchange_purchase_auto_complete()
        self.assertEqual(self.invoice_01.journal_id, self.journal_01)

    def test_03(self):
        """
        Data:
            - A draft invoice
            - A confirmed purchase order with a fiscal position
            - Two purchase journals allowed on the fiscal position
        Test case:
            - Set the purchase order on the invoice
        Expected result:
            - The journal of the invoice didn't change
        """
        self.fiscal_position_01.allowed_journal_ids = [
            (6, 0, (self.journal_01 | self.journal_02).ids)
        ]
        self.invoice_01.purchase_id = self.purchase_order_01
        self.invoice_01._onchange_purchase_auto_complete()
        self.assertEqual(self.invoice_01.journal_id, self.journal_01)
