# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time

from odoo import SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tests import common, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "-at_install")
class TestPurchaseRequestType(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pr_obj = cls.env["purchase.request"]
        cls.company_obj = cls.env["res.company"]
        # Products
        cls.product1 = cls.env.ref("product.product_product_7")
        cls.product2 = cls.env.ref("product.product_product_9")
        cls.product3 = cls.env.ref("product.product_product_11")
        # Purchase Request Type
        cls.type1 = cls.env.ref("purchase_request_type.pr_type_regular")
        cls.type2 = cls.env.ref("purchase_request_type.pr_type_reduce_step")
        # Picking Type
        cls.picking_type = cls.env.ref("stock.picking_type_in")
        cls.picking_type2 = cls.env.ref("stock.picking_type_internal")
        cls.type2.picking_type_id = cls.picking_type
        cls.company2 = cls.company_obj.create({"name": "company2"})

    def test_purchase_request_type(self):
        purchase_request = self._create_purchase_request(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )
        self.assertEqual(purchase_request.request_type, self.type1)
        purchase_request.onchange_request_type()
        self.assertEqual(purchase_request.picking_type_id, self.picking_type2)

    def _create_purchase_request(self, line_products):
        """Create a purchase request.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                "name": product.name,
                "product_id": product.id,
                "product_qty": qty,
                "product_uom_id": product.uom_id.id,
                "estimated_cost": 100,
                "date_required": time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            }
            lines.append((0, 0, line_values))
        purchase_request = self.pr_obj.create(
            {
                "request_type": self.type1.id,
                "picking_type_id": self.picking_type2.id,
                "line_ids": lines,
            }
        )
        return purchase_request

    def test_purchase_request_change_company(self):
        request = self.pr_obj.new({"requested_by": SUPERUSER_ID})
        self.assertEqual(request.request_type, self.type1)
        request._onchange_company()
        self.assertFalse(request.request_type)

    def test_compute_purchase_request_type(self):
        request1 = self.pr_obj.new({"request_type": self.type1.id})
        request2 = self.pr_obj.new({"request_type": self.type2.id})
        self.assertFalse(request1.reduce_step)
        self.assertEqual(request2.reduce_step, self.type2.reduce_step)

    def test_purchase_request_type_company_error(self):
        self.type1.company_id = self.env.company
        request = self.pr_obj.create({"picking_type_id": self.picking_type.id})
        self.assertEqual(request.company_id, self.type1.company_id)
        with self.assertRaises(ValidationError):
            request.write({"company_id": self.company2.id})
