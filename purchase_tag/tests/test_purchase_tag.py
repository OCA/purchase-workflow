import psycopg2.errors as errors

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestPurchaseTag(TransactionCase):
    def setUp(self):
        super().setUp()
        self.PurchaseTag = self.env["purchase.tag"]

    def test_create_purchase_tag(self):
        tag = self.PurchaseTag.create({"name": "Test Tag"})
        self.assertEqual(tag.name, "Test Tag")
        self.assertTrue(tag.color)

    def test_unique_tag_name(self):
        unique_name = "Unique Tag "
        self.PurchaseTag.create({"name": unique_name})
        with (
            mute_logger("odoo.sql_db"),
            self.assertRaises(errors.UniqueViolation),
            self.assertRaises(ValidationError),
            self.cr.savepoint(),
        ):
            self.PurchaseTag.create({"name": unique_name})

    def test_search_display_name(self):
        tag = self.PurchaseTag.create({"name": "Search Tag"})
        result_ids = self.PurchaseTag._search_display_name("ilike", "Search Tag")
        self.assertIn(tag.id, result_ids)

    def test_check_parent_recursion(self):
        parent_tag = self.PurchaseTag.create({"name": "Parent Tag"})
        child_tag = self.PurchaseTag.create(
            {"name": "Child Tag", "parent_id": parent_tag.id}
        )
        with self.assertRaises(UserError):
            parent_tag.write({"parent_id": child_tag.id})

    def test_search_display_name_with_parent(self):
        parent_tag = self.PurchaseTag.create({"name": "Parent Tag"})
        child_tag = self.PurchaseTag.create(
            {"name": "Child Tag", "parent_id": parent_tag.id}
        )
        result = self.PurchaseTag._search_display_name(
            "ilike", "Parent Tag / Child Tag"
        )
        self.assertIn(child_tag.id, self.PurchaseTag.search(result).ids)
