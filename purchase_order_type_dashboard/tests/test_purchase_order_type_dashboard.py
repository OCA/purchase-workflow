# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time

from odoo.tests import common, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "-at_install")
class TestPurchaseOrderTypeDashboard(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_obj = cls.env["purchase.order"]
        # Partner
        cls.partner1 = cls.env.ref("base.res_partner_1")
        # Products
        cls.product1 = cls.env.ref("product.product_product_7")
        cls.product2 = cls.env.ref("product.product_product_9")
        cls.product3 = cls.env.ref("product.product_product_11")
        # Purchase Type
        cls.type1 = cls.env.ref("purchase_order_type.po_type_regular")

    def test_purchase_order_type_dashboard(self):
        po_type1_rfq_count = self.type1.state_rfq_po_count
        purchase = self._create_purchase(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )
        self.assertEquals(self.type1.state_rfq_po_count, po_type1_rfq_count + 1)

        purchase.button_confirm()
        po_type1_is_no_count = self.type1.invoice_status_no_po_count
        po_type1_is_ti_count = self.type1.invoice_status_ti_po_count
        purchase_picking = purchase.picking_ids
        for move in purchase_picking.move_ids_without_package:
            move.move_line_ids.write({"qty_done": move.purchase_line_id.product_qty})
        purchase_picking.action_done()
        self.assertEquals(
            self.type1.invoice_status_no_po_count, po_type1_is_no_count - 1
        )
        self.assertEquals(
            self.type1.invoice_status_ti_po_count, po_type1_is_ti_count + 1
        )

    def _create_purchase(self, line_products):
        """ Create a purchase order.
        ``line_products`` is a list of tuple [(product, qty)]
        """
        lines = []
        for product, qty in line_products:
            line_values = {
                "name": product.name,
                "product_id": product.id,
                "product_qty": qty,
                "product_uom": product.uom_id.id,
                "price_unit": 100,
                "date_planned": time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            }
            lines.append((0, 0, line_values))
        purchase = self.po_obj.create(
            {
                "partner_id": self.partner1.id,
                "order_type": self.type1.id,
                "order_line": lines,
            }
        )
        return purchase
