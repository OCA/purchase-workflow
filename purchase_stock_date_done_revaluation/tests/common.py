# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon

# Rates expressed as units of the foreign currency per 1 unit of company
# currency, so a foreign -> company conversion divides by the rate.
DATE_1 = "2026-03-01"  # rate 1.0  -> 1000 (company) for 1000 (foreign)
DATE_2 = "2026-03-10"  # rate 2.0  ->  500 (company) for 1000 (foreign)


class PurchaseStockDateDoneRevaluationCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.group_ids = [
            Command.link(cls.env.ref("stock.group_stock_manager").id)
        ]
        cls.foreign_currency = cls._setup_foreign_currency()
        # ``periodic`` valuation: move.value is still computed (FX applied) but
        # no perpetual journal entries are posted, so no stock valuation
        # accounts are required to run these tests.
        categ = cls.env["product.category"].create(
            {
                "name": "FIFO Periodic",
                "property_cost_method": "fifo",
                "property_valuation": "periodic",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Revaluation Product",
                "is_storable": True,
                "categ_id": categ.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

    @classmethod
    def _setup_foreign_currency(cls):
        currency = cls.env.ref("base.EUR")
        if currency == cls.company.currency_id:
            currency = cls.env.ref("base.USD")
        currency.active = True
        cls.env["res.currency.rate"].search(
            [
                ("currency_id", "=", currency.id),
                ("company_id", "in", [False, cls.company.id]),
            ]
        ).unlink()
        cls.env["res.currency.rate"].create(
            [
                {
                    "name": DATE_1,
                    "rate": 1.0,
                    "currency_id": currency.id,
                    "company_id": cls.company.id,
                },
                {
                    "name": DATE_2,
                    "rate": 2.0,
                    "currency_id": currency.id,
                    "company_id": cls.company.id,
                },
            ]
        )
        return currency

    def _receive_po(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "currency_id": self.foreign_currency.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_qty": 10.0,
                            "price_unit": 100.0,
                            "name": self.product.name,
                            "product_uom_id": self.product.uom_id.id,
                        }
                    )
                ],
            }
        )
        po.button_confirm()
        receipt = po.picking_ids[0]
        receipt.move_ids.quantity = 10.0
        receipt.move_ids.picked = True
        receipt.button_validate()
        return po, receipt, receipt.move_ids
