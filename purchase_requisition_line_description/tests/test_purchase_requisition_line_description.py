# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import html

from odoo.tests import common

from ..hooks import post_init_hook


class TestPurchaseRequisitionLineDescription(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "standard_price": 10,
                "description_purchase": "description for purchase",
            }
        )
        cls.product_no_description = cls.env["product.product"].create(
            {"name": "Product without description"}
        )

    def test_compute_product_description_name(self):
        """Test that product description is computed using product and vendor."""
        requisition = self.env["purchase.requisition"].create(
            {
                "vendor_id": self.partner.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(requisition.line_ids[0].name, "description for purchase")

    def test_section_note_and_edited_names_are_kept(self):
        requisition = self.env["purchase.requisition"].create(
            {
                "vendor_id": self.partner.id,
                "line_ids": [
                    (0, 0, {"display_type": "line_section", "name": "Section A"}),
                    (0, 0, {"product_id": self.product_no_description.id}),
                    (0, 0, {"display_type": "line_note", "name": "A note"}),
                ],
            }
        )
        section, line, note = requisition.line_ids
        requisition.line_ids._compute_name()
        self.assertEqual(section.name, "Section A")
        self.assertEqual(note.name, "A note")
        self.assertFalse(line.name)
        line.name = "Edited description"
        self.assertEqual(line.name, "Edited description")
        line.product_id = self.product
        self.assertEqual(line.name, "description for purchase")

    def test_report_description_column(self):
        requisition = self.env["purchase.requisition"].create(
            {
                "vendor_id": self.partner.id,
                "line_ids": [
                    (0, 0, {"display_type": "line_section", "name": "Section A"}),
                    (0, 0, {"product_id": self.product.id, "product_qty": 1}),
                ],
            }
        )
        content, _ = self.env["ir.actions.report"]._render_qweb_html(
            "purchase_requisition.action_report_purchase_requisitions",
            requisition.ids,
        )
        doc = html.fromstring(content)
        self.assertIn("description for purchase", doc.text_content())
        # The section row spans as many columns as the header has
        header = doc.xpath("//table//thead//th")
        section = doc.xpath("//tr[@name='tr_section']/td")
        product = doc.xpath("//tr[@name='tr_product']/td")
        self.assertEqual(sum(int(td.get("colspan", 1)) for td in section), len(header))
        self.assertEqual(len(product), len(header))

    def test_post_init_hook_fills_empty_lines(self):
        requisition = self.env["purchase.requisition"].create(
            {
                "vendor_id": self.partner.id,
                "line_ids": [
                    (0, 0, {"product_id": self.product.id}),
                    (0, 0, {"product_id": self.product_no_description.id}),
                ],
            }
        )
        empty, edited = requisition.line_ids
        empty.name = False
        edited.name = "Typed by the user"
        post_init_hook(self.env)
        self.assertEqual(empty.name, "description for purchase")
        self.assertEqual(edited.name, "Typed by the user")
