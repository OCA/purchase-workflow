# Copyright 2026 PopSolutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestPurchaseRequestLineSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product for the request", "type": "consu"}
        )
        cls.request = cls.env["purchase.request"].create(
            {"requested_by": cls.env.user.id}
        )

    def _add_line(self, name, **vals):
        return self.env["purchase.request.line"].create(
            dict(
                {
                    "request_id": self.request.id,
                    "product_id": self.product.id,
                    "name": name,
                    "product_qty": 1.0,
                },
                **vals,
            )
        )

    def test_lines_keep_the_order_they_were_typed_in(self):
        """Without this module the order is id desc and the newest line
        shows up first. Sharing the same default sequence, the lines now
        fall back to id, so they read in the order they were typed."""
        first = self._add_line("first")
        second = self._add_line("second")
        third = self._add_line("third")
        self.assertEqual(self.request.line_ids.ids, [first.id, second.id, third.id])

    def test_new_lines_get_the_default_sequence(self):
        line = self._add_line("only one")
        self.assertEqual(line.sequence, 10)

    def test_sequence_drives_the_order(self):
        first = self._add_line("first")
        second = self._add_line("second")
        second.sequence = 5
        self.request.invalidate_recordset(["line_ids"])
        self.assertEqual(self.request.line_ids.ids, [second.id, first.id])

    def test_line_number_follows_the_position(self):
        first = self._add_line("first")
        second = self._add_line("second")
        self.assertEqual(first.line_number, 1)
        self.assertEqual(second.line_number, 2)

        second.sequence = 1
        self.request.invalidate_recordset(["line_ids"])
        first.invalidate_recordset(["line_number"])
        second.invalidate_recordset(["line_number"])
        self.assertEqual(second.line_number, 1)
        self.assertEqual(first.line_number, 2)

    def test_line_number_is_renumbered_when_a_line_is_removed(self):
        first = self._add_line("first")
        second = self._add_line("second")
        third = self._add_line("third")
        self.assertEqual(third.line_number, 3)

        second.unlink()
        self.request.invalidate_recordset(["line_ids"])
        third.invalidate_recordset(["line_number"])
        self.assertEqual(first.line_number, 1)
        self.assertEqual(third.line_number, 2)

    def test_line_number_is_zero_without_a_request(self):
        """Defensive: the field must not raise on an orphan line."""
        line = self.env["purchase.request.line"].new(
            {"product_id": self.product.id, "name": "orphan"}
        )
        self.assertEqual(line.line_number, 0)

    def test_line_numbers_of_two_requests_do_not_mix(self):
        other_request = self.env["purchase.request"].create(
            {"requested_by": self.env.user.id}
        )
        mine = self._add_line("mine")
        theirs = self.env["purchase.request.line"].create(
            {
                "request_id": other_request.id,
                "product_id": self.product.id,
                "name": "theirs",
                "product_qty": 1.0,
            }
        )
        lines = mine | theirs
        lines.invalidate_recordset(["line_number"])
        self.assertEqual(mine.line_number, 1)
        self.assertEqual(theirs.line_number, 1)
