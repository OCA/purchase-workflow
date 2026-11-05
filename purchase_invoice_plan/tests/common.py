# Copyright 2019 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import Command, fields
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseInvoicePlanCommon(BaseCommon):
    _test_user_groups = (
        "purchase.group_purchase_user",
        "stock.group_stock_user",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PurchaseInvoicePlan = cls.env["purchase.create.invoice.plan"]

        cls.test_partner = cls.partner
        cls.test_service = cls.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
            }
        )
        cls.test_product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )

        cls.test_po_product = cls.env["purchase.order"].create(
            {
                "partner_id": cls.test_partner.id,
                "use_invoice_plan": True,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "PO-Product",
                            "product_id": cls.test_product.id,
                            "date_planned": fields.Datetime.now(),
                            "product_qty": 10,
                            "uom_id": cls.test_product.uom_id.id,
                            "price_unit": 1000,
                            "tax_ids": False,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _create_purchase_order(cls, product, product_qty, price_unit, company=None):
        env = cls.env(su=True) if company else cls.env
        return env["purchase.order"].create(
            {
                "partner_id": cls.test_partner.id,
                "company_id": (company or cls.env.company).id,
                "use_invoice_plan": True,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_qty": product_qty,
                            "price_unit": price_unit,
                            "tax_ids": False,
                        }
                    )
                ],
            }
        )

    def _create_plan_purchase(self, price_unit=1000, company=None):
        """Purchase order of 10 units with 5 monthly installments"""
        purchase = self._create_purchase_order(
            self.test_product, 10, price_unit, company=company
        )
        purchase.create_invoice_plan(5, fields.Date.today(), 1, "month")
        return purchase

    def _create_invoice_plan(self, purchase, num_installment):
        with Form(self.PurchaseInvoicePlan) as p:
            p.num_installment = num_installment
        purchase_plan = p.save()
        purchase_plan.with_context(
            active_id=purchase.id, active_ids=purchase.ids
        ).purchase_create_invoice_plan()

    def _receive(self, purchase, quantity):
        receive = purchase.picking_ids.filtered(lambda pick: pick.state != "done")
        receive.move_ids.quantity = quantity
        receive.with_context(skip_backorder=True).button_validate()

    def _create_bill_by_plan(self, purchase, all_remain=False):
        """Create Bill by Plan button of the purchase order"""
        self.env["purchase.make.planned.invoice"].with_context(
            active_id=purchase.id, all_remain_invoices=all_remain
        ).create({}).create_invoices_by_plan()

    def _create_bills(self, purchases):
        """Create Bills button of the purchase list view"""
        action = purchases.action_create_invoice()
        return self.env["account.move"].browse(action["res_id"])
