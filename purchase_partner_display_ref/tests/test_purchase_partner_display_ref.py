# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from lxml import etree

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchasePartnerDisplayRef(TransactionCase):
    """The Purchase views must inject ``partner_display_ref_field='supplier_ref'``
    into the vendor ``partner_id`` field context. The decoration mechanism itself
    is covered by the ``partner_display_ref`` base module's tests.
    """

    def _partner_id_contexts(self, xmlid):
        view = self.env.ref(xmlid)
        tree = etree.fromstring(view.get_combined_arch())
        fields = tree.xpath("//field[@name='partner_id']")
        self.assertTrue(fields, f"{xmlid} must contain a partner_id field")
        return [
            ast.literal_eval(field.get("context"))
            for field in fields
            if field.get("context")
        ]

    def _assert_supplier_ref(self, xmlid):
        self.assertTrue(
            any(
                ctx.get("partner_display_ref_field") == "supplier_ref"
                for ctx in self._partner_id_contexts(xmlid)
            ),
            f"{xmlid} must inject partner_display_ref_field='supplier_ref' into "
            f"the partner_id context",
        )

    def test_order_form_injects_context(self):
        self._assert_supplier_ref("purchase.purchase_order_form")

    def test_order_form_preserves_existing_context_keys(self):
        contexts = self._partner_id_contexts("purchase.purchase_order_form")
        merged = next(
            ctx
            for ctx in contexts
            if ctx.get("partner_display_ref_field") == "supplier_ref"
        )
        self.assertEqual(merged.get("res_partner_search_mode"), "supplier")
        self.assertTrue(merged.get("show_vat"))

    def test_purchase_filter_injects_context(self):
        self._assert_supplier_ref("purchase.view_purchase_order_filter")

    def test_kpis_tree_injects_context(self):
        self._assert_supplier_ref("purchase.purchase_order_kpis_tree")
