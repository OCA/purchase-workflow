# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "Transit Warehouse", "code": "TWH"}
        )
        cls.other_type = cls.warehouse.in_type_id.copy({"name": "Other Receipts"})
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.transit_incoterm = cls.env["account.incoterms"].create(
            {"name": "Transit", "code": "TT1", "transit_receipt": True}
        )
        cls.incoterm = cls.env["account.incoterms"].create(
            {"name": "No transit", "code": "TT2"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "is_storable": True}
        )

    def _create_purchase(self, incoterm, picking_type=None):
        return self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "incoterm_id": incoterm.id,
                "picking_type_id": (picking_type or self.warehouse.in_type_id).id,
                "order_line": [
                    Command.create({"product_id": self.product.id, "product_qty": 1})
                ],
            }
        )

    def test_transit_incoterm(self):
        with Form(self.env["purchase.order"]) as purchase_form:
            purchase_form.partner_id = self.supplier
            purchase_form.picking_type_id = self.warehouse.in_type_id
            purchase_form.incoterm_id = self.transit_incoterm
            self.assertEqual(
                purchase_form.picking_type_id, self.warehouse.transit_in_type_id
            )
            purchase_form.incoterm_id = self.incoterm
            self.assertEqual(purchase_form.picking_type_id, self.warehouse.in_type_id)

    def test_create_without_picking_type(self):
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "incoterm_id": self.transit_incoterm.id,
            }
        )
        warehouse = purchase.picking_type_id.warehouse_id
        self.assertTrue(warehouse)
        self.assertEqual(purchase.picking_type_id, warehouse.transit_in_type_id)

    def test_create_without_incoterm(self):
        purchase = self.env["purchase.order"].create({"partner_id": self.supplier.id})
        self.assertEqual(
            purchase.picking_type_id, purchase.picking_type_id.warehouse_id.in_type_id
        )

    def test_incoterm_change(self):
        purchase = self._create_purchase(self.incoterm)
        self.assertEqual(purchase.picking_type_id, self.warehouse.in_type_id)
        purchase.incoterm_id = self.transit_incoterm
        self.assertEqual(purchase.picking_type_id, self.warehouse.transit_in_type_id)
        purchase.incoterm_id = self.incoterm
        self.assertEqual(purchase.picking_type_id, self.warehouse.in_type_id)

    def test_manual_choice_kept(self):
        purchase = self._create_purchase(self.transit_incoterm)
        purchase.picking_type_id = self.warehouse.in_type_id
        purchase.date_planned = "2026-11-01"
        self.assertEqual(purchase.picking_type_id, self.warehouse.in_type_id)
        purchase.incoterm_id = self.incoterm
        purchase.incoterm_id = self.transit_incoterm
        self.assertEqual(purchase.picking_type_id, self.warehouse.transit_in_type_id)

    def test_other_picking_type_kept(self):
        purchase = self._create_purchase(self.incoterm, self.other_type)
        self.assertEqual(purchase.picking_type_id, self.other_type)
        purchase.partner_id = self.env["res.partner"].create({"name": "Other"})
        self.assertEqual(purchase.picking_type_id, self.other_type)

    def test_reception_unchanged(self):
        purchase = self._create_purchase(self.incoterm)
        purchase.button_confirm()
        self.assertEqual(
            purchase.picking_ids.picking_type_id, self.warehouse.in_type_id
        )
        self.assertEqual(
            purchase.picking_ids.location_dest_id, self.warehouse.lot_stock_id
        )
