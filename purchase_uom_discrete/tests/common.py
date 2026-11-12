# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import TransactionCase


class PurchaseUomDiscreteCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids = [Command.link(cls.env.ref("uom.group_uom").id)]
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.uom_pack_6 = cls._create_uom("Pack of 6", 6.0, cls.uom_unit)
        cls.product_unit = cls._create_product("Discrete Unit Product")
        cls.product_pack = cls._create_product(
            "Discrete Pack Product", uom=cls.uom_pack_6
        )
        cls.product_kg = cls._create_product("Continuous Kg Product", uom=cls.uom_kg)

    @classmethod
    def _create_uom(cls, name, factor, relative_uom_id):
        """Create a UoM relative to another UoM.

        :param str name: name of the UoM to create.
        :param float factor: factor relative to ``relative_uom_id``.
        :param recordset relative_uom_id: parent UoM in the hierarchy.
        :return: created UoM.
        """
        return cls.env["uom.uom"].create(
            {
                "name": name,
                "relative_factor": factor,
                "relative_uom_id": relative_uom_id.id,
            }
        )

    @classmethod
    def _create_product(cls, name, uom=None):
        """Create a purchasable product.

        :param str name: name of the product to create.
        :param recordset uom: optional product default UoM.
        :return: created product variant.
        """
        vals = {
            "name": name,
            "type": "consu",
            "purchase_ok": True,
        }
        if uom:
            vals["uom_id"] = uom.id
        return cls.env["product.product"].create(vals)
