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
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]
        cls.AccountInvoice = cls.env["account.move"]
        cls.AccountInvoiceLine = cls.env["account.move.line"]
        cls.partner_id = cls.env.ref("base.res_partner_1")
        cls.product_id_1 = cls.env.ref("product.product_product_8")
        cls.product_id_2 = cls.env.ref("product.product_product_11")
        cls.category = cls.env.ref("product.product_category_1").copy(
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
    def _create_purchase_order(cls, **kwargs):
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
                        "product_uom": cls.product_id_1.uom_po_id.id,
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
                        "product_uom": cls.product_id_2.uom_po_id.id,
                        "price_unit": 250.0,
                        "date_planned": datetime.today(),
                    },
                ),
            ],
        }
        po_vals.update(kwargs)
        return cls.PurchaseOrder.create(po_vals)
