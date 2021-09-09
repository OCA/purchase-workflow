# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.purchase_landed_cost.tests.test_purchase_landed_cost import (
    TestPurchaseLandedCostBase,
)


class TestLandedCostVolumetricWeight(TestPurchaseLandedCostBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.type_volume = cls.env["purchase.expense.type"].create(
            {
                "name": "Type Volumetric weight",
                "calculation_method": "volumetric_weight",
            }
        )
        cls.product.write(
            {"volume": 1, "dimensional_uom_id": cls.env.ref("uom.product_uom_meter").id}
        )
        cls._import_invoice_line_wizard(cls, cls.type_volume)

    def test_distribution_import_shipment(self):
        wiz = (
            self.env["picking.import.wizard"]
            .with_context(active_id=self.distribution.id)
            .create(
                {"supplier": self.supplier.id, "pickings": [(6, 0, self.picking.ids)]}
            )
        )
        wiz.action_import_picking()
        self.distribution.action_calculate()
        self.assertEqual(self.distribution.total_volumetric_weight, 500)
        self.assertEqual(self.distribution.total_expense, 10)
