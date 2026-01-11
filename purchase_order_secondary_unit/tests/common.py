# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseSecondaryUnitCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id = [Command.link(cls.env.ref("uom.group_uom").id)]
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].create(
            {
                "name": "unit-700",
                "uom_id": cls.product_uom_unit.id,
                "factor": 0.7,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.product.purchase_secondary_uom_id = cls.secondary_unit
        cls.partner = cls.env["res.partner"].create({"name": "Test Vendor"})
