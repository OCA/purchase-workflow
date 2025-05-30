from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseTag(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        PurchaseTag = cls.env["purchase.tag"]
        cls.tag_parent = PurchaseTag.create({"name": "Parent"})
        cls.tag_child = PurchaseTag.create(
            {"name": "Child", "parent_id": cls.tag_parent.id}
        )
        cls.tag_grandchild = PurchaseTag.create(
            {"name": "Grandchild", "parent_id": cls.tag_child.id}
        )

    def test_display_name_computation(self):
        # Verify the hierarchical display_name.
        self.assertEqual(
            self.tag_grandchild.display_name, "Parent / Child / Grandchild"
        )
        self.assertEqual(self.tag_child.display_name, "Parent / Child")
        self.assertEqual(self.tag_parent.display_name, "Parent")

    def test_name_search(self):
        # Perform a search using part of the display_name.
        results = self.env["purchase.tag"].name_search(name="Grandchild")
        self.assertTrue(results)
        self.assertEqual(results[0][0], self.tag_grandchild.id)
        self.assertEqual(results[0][1], "Parent / Child / Grandchild")

    def test_recursion_error(self):
        # Trigger recursion to raise a UserError from Odoo's core.
        with self.assertRaisesRegex(UserError, "Recursion Detected."):
            self.tag_parent.write({"parent_id": self.tag_grandchild.id})
