# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.addons.base.tests.common import BaseCommon


class PurchaseOrderLineSequenceCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Useful models
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.partner_id = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        product_uom_unit_round_1 = cls.env.ref("uom.product_uom_unit")
        cls.product_id_1 = cls.env["product.product"].create(
            {
                "name": "Large Desk",
                "standard_price": 1299.0,
                "list_price": 1799.0,
                "type": "consu",
                "weight": 9.54,
                "default_code": "E-COM09",
                "description_sale": "Minimalist wooden desk for executive use",
                "uom_id": product_uom_unit_round_1.id,
            }
        )

        cls.product_id_2 = cls.env["product.product"].create(
            {
                "name": "Conference Chair",
                "standard_price": 28.0,
                "list_price": 33.0,
                "type": "consu",
                "uom_id": product_uom_unit_round_1.id,
            }
        )

        cls.AccountInvoice = cls.env["account.move"]
        cls.AccountInvoiceLine = cls.env["account.move.line"]

        cls.category = cls.env["product.category"].create(
            {
                "name": "Test category",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
            }
        )

        cls.account_expense = cls.env["account.account"].create(
            {
                "name": "Expense",
                "code": "EXP00",
                "account_type": "liability_current",
                "reconcile": True,
            }
        )
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Payable",
                "code": "PAY00",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )

        cls.category.property_account_expense_categ_id = cls.account_expense

        cls.category.property_stock_journal = cls.env["account.journal"].create(
            {"name": "Stock journal", "type": "sale", "code": "STK00"}
        )
        cls.product_id_1.categ_id = cls.category
        cls.product_id_2.categ_id = cls.category
        cls.partner_id.property_account_payable_id = cls.account_payable

    @classmethod
    def _create_purchase_order(cls):
        po_vals = {
            "partner_id": cls.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product_id_1.name,
                        "product_id": cls.product_id_1.id,
                        "product_qty": 5.0,
                        "product_uom_id": cls.product_id_1.uom_id.id,
                        "price_unit": 500.0,
                        "date_planned": datetime.today(),
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": cls.product_id_2.name,
                        "product_id": cls.product_id_2.id,
                        "product_qty": 5.0,
                        "product_uom_id": cls.product_id_2.uom_id.id,
                        "price_unit": 250.0,
                        "date_planned": datetime.today(),
                    },
                ),
            ],
        }

        return cls.PurchaseOrder.create(po_vals)
