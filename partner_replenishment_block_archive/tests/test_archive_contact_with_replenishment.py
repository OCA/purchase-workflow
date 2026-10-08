# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestArchiveContactWithReplenishment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_id = cls.env.ref("base.main_company")
        cls.product_id = cls.env.ref("product.product_product_7")
        cls.location_id = cls.env.ref("stock.stock_location_stock")
        cls.supplier_id = cls.env.ref("base.res_partner_12")
        cls.orderpoint_id = cls.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": cls.product_id.id,
                "location_id": cls.location_id.id,
                "qty_on_hand": 10,
                "supplier_id": cls.supplier_id.id,
                "company_id": cls.company_id.id,
            }
        )

    def test_archive_contact(self):
        with self.assertRaises(ValidationError):
            self.supplier_id.write({"active": False})
