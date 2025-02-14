# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.stock.tests import common


class TestProcurementPurchaseRequisitionGeneration(BaseCommon, common.TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.vendor = cls.env["res.partner"].create({"name": "Test vendor"})
        cls.productA.write(
            {
                "purchase_requisition": "tenders",
                "seller_ids": [(0, 0, {"partner_id": cls.vendor.id})],
                "route_ids": [(6, 0, [cls.buy.id, cls.mto.id])],
            }
        )
        cls.productB.write(
            {
                "purchase_requisition": "tenders",
                "route_ids": [(6, 0, [cls.buy.id, cls.mto.id])],
            }
        )
        cls.origin = "TEST"
        cls.group = cls.env["procurement.group"].create({"name": "Test"})
        cls.values = {"date_planned": fields.Datetime.now(), "group_id": cls.group}
        cls.stock_rule = cls.buy.rule_ids[0]

    def _set_procurement_by_product(self, group, product):
        location = self.env["stock.location"].browse(self.stock_location)
        procurement = group.Procurement(
            product,
            1,
            product.uom_id,
            location,
            False,
            self.origin,
            self.env.company,
            self.values,
        )
        rule = group._get_rule(
            procurement.product_id, procurement.location_id, procurement.values
        )
        return (procurement, rule)

    def _run_procurements(self):
        self.stock_rule._run_buy(
            [
                self._set_procurement_by_product(self.group, self.productA),
                self._set_procurement_by_product(self.group, self.productB),
            ]
        )

    @mute_logger("odoo.models.unlink")
    def test_product_replenish(self):
        self.env["purchase.requisition"].search([("state", "=", "draft")]).unlink()
        wizard_form = Form(
            self.env["product.replenish"].with_context(
                default_product_tmpl_id=self.productA.product_tmpl_id.id
            )
        )
        wizard_form.route_id = self.buy
        wizard_form.supplier_id = self.productA.seller_ids
        wizard = wizard_form.save()
        res = wizard.launch_replenishment()
        links = res.get("params", {}).get("links")
        url = links and links[0].get("url", "") or ""
        purchase_requisition_id, model_name = self.url_extract_rec_id_and_model(url)
        purchase_requisition_id = int(purchase_requisition_id[0])
        model_name = model_name[0]
        self.assertEqual(model_name, "purchase.requisition")
        requisition = self.env[model_name].browse(purchase_requisition_id)
        self.assertEqual(requisition.state, "draft")
        self.assertTrue(requisition.procurement_group_id)
        self.assertIn(self.productA, requisition.line_ids.product_id)

    @mute_logger("odoo.models.unlink")
    def test_purchase_requisition_grouped(self):
        domain = [("state", "=", "draft")]
        self.env["purchase.requisition"].search(domain).unlink()
        self._run_procurements()
        items = self.env["purchase.requisition"].search(domain)
        self.assertEqual(len(items), 1)
        self.assertEqual(items.origin, self.origin)
        products = items.line_ids.mapped("product_id")
        self.assertIn(self.productA, products)
        self.assertIn(self.productB, products)
