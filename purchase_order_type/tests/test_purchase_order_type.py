# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time

from odoo.exceptions import ValidationError
from odoo.tests import common, tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "-at_install")
class TestPurchaseOrderType(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.po_obj = cls.env["purchase.order"]
        cls.company_obj = cls.env["res.company"]
        # Partner
        cls.partner1 = cls.env["res.partner"].create({"name": "POType Partner 1"})
        # Products
        cls.product1 = cls.env["product.product"].create(
            {"name": "POType Product 1", "type": "consu"}
        )
        cls.product2 = cls.env["product.product"].create(
            {"name": "POType Product 2", "type": "consu"}
        )
        cls.product3 = cls.env["product.product"].create(
            {"name": "POType Product 3", "type": "consu"}
        )
        # Purchase Type
        cls.type1 = cls.env.ref("purchase_order_type.po_type_regular")
        cls.type2 = cls.env.ref("purchase_order_type.po_type_planned")
        # Payment Term
        cls.payterm = cls.env.ref("account.account_payment_term_immediate")
        # Incoterm
        cls.incoterm = cls.env.ref("account.incoterm_EXW")
        cls.type2.payment_term_id = cls.payterm
        cls.type2.incoterm_id = cls.incoterm
        cls.partner1.purchase_type = cls.type2
        cls.company2 = cls.company_obj.create({"name": "company2"})

    def test_purchase_order_type(self):
        purchase = self._create_purchase(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )
        self.assertEqual(purchase.order_type, self.type1)
        self.assertFalse(purchase.incoterm_id)
        self.assertFalse(purchase.payment_term_id)
        # partner1 has its own purchase_type (type2) - onchange_partner_id
        # overwrites the explicitly-set type1 with it.
        purchase.onchange_partner_id()
        self.assertEqual(purchase.order_type, self.type2)
        purchase.onchange_order_type()
        self.assertEqual(purchase.incoterm_id, self.incoterm)
        self.assertEqual(purchase.payment_term_id, self.payterm)

    def _create_purchase(self, line_products):
        """Create a purchase order.
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

    def test_purchase_order_change_company(self):
        order = self.po_obj.new({"partner_id": self.partner1.id})
        order.onchange_partner_id()
        self.assertEqual(order.order_type, self.type2)
        order._onchange_company()
        self.assertEqual(order.order_type, self.type2)
        order.write({"order_type": False})
        order._onchange_company()
        # _onchange_company resolves via the same partner-then-company
        # priority as onchange_partner_id: partner1 has its own type, so
        # that wins over the (here, unconfigured) company default.
        self.assertEqual(order.order_type, self.type2)

    def test_purchase_order_type_company_error(self):
        order = self.po_obj.create(
            {"partner_id": self.partner1.id, "order_type": self.type1.id}
        )
        self.assertEqual(order.order_type, self.type1)
        self.assertEqual(order.company_id, self.type1.company_id)
        with self.assertRaises(ValidationError):
            order.write({"company_id": self.company2.id})

    def test_order_type_from_partner(self):
        lines = []
        line_values = {
            "name": self.product1.name,
            "product_id": self.product1.id,
            "product_qty": 3,
            "product_uom": self.product1.uom_id.id,
            "price_unit": 100,
        }
        lines.append((0, 0, line_values))
        type_from_partner = self.po_obj.create(
            {
                "partner_id": self.partner1.id,
                "order_line": lines,
            }
        )

        # Check if set order_type on create
        self.assertEqual(type_from_partner.order_type, self.partner1.purchase_type)

        # order_type is no longer a compute: a plain write() to partner_id
        # does not re-derive it any more, only the form (onchange) and
        # create() do. This is a deliberate behavior change - partner-driven
        # derivation via write() alone is no longer supported.
        partner2 = self.env["res.partner"].create({"name": "POType Partner 2"})
        partner2.purchase_type = self.type1
        type_from_partner.write({"partner_id": partner2.id})
        self.assertEqual(
            type_from_partner.order_type,
            self.type2,
            "a plain write() to partner_id must not touch order_type",
        )

    def test_order_type_from_partner_via_onchange(self):
        """onchange_partner_id overwrites whenever the vendor has a type of
        its own, and only leaves an already-set type alone when the new
        vendor has nothing to offer - it never clears it."""
        order = self.po_obj.new({"partner_id": self.partner1.id})
        order.onchange_partner_id()
        self.assertEqual(order.order_type, self.type2)

        partner2 = self.env["res.partner"].create({"name": "POType Partner 2"})
        partner2.purchase_type = self.type1
        order.partner_id = partner2
        order.onchange_partner_id()
        # partner2 has its own type - it overwrites type2.
        self.assertEqual(order.order_type, self.type1)

        partner_without_type = self.env["res.partner"].create(
            {"name": "POType Partner Without Type"}
        )
        order.partner_id = partner_without_type
        order.onchange_partner_id()
        # partner_without_type has nothing to offer - the existing type1 is
        # left untouched, not cleared.
        self.assertEqual(order.order_type, self.type1)

    def test_partner_cleared_clears_order_type_via_onchange(self):
        order = self.po_obj.new({"partner_id": self.partner1.id})
        order.onchange_partner_id()
        self.assertTrue(order.order_type)
        order.partner_id = False
        order.onchange_partner_id()
        self.assertFalse(order.order_type)


@tagged("post_install", "-at_install")
class TestPurchaseOrderTypeDefault(common.TransactionCase):
    """Coverage for the ``is_default`` fallback and the third gap found:
    payment_term_id/incoterm_id following order_type on ``create()``, not
    just via the form's ``onchange_order_type``.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company
        # Demo data flags po_type_regular as the default for cls.company -
        # cleared so each test below starts from "nothing configured" and
        # controls is_default itself without tripping the one-default-per-
        # company constraint.
        cls.env["purchase.order.type"].search(
            [("is_default", "=", True)]
        ).is_default = False
        cls.other_company = cls.env["res.company"].create(
            {"name": "POType Default Other Company"}
        )
        cls.vendor_with_type = cls.env["res.partner"].create(
            {"name": "POType Default Vendor With Type"}
        )
        cls.vendor_without_type = cls.env["res.partner"].create(
            {"name": "POType Default Vendor Without Type"}
        )
        cls.payterm = cls.env.ref("account.account_payment_term_immediate")
        cls.incoterm = cls.env.ref("account.incoterm_EXW")
        cls.vendor_type = cls.env["purchase.order.type"].create(
            {
                "name": "POType Default Vendor Type",
                "company_id": cls.company.id,
                "payment_term_id": cls.payterm.id,
                "incoterm_id": cls.incoterm.id,
            }
        )
        cls.vendor_with_type.purchase_type = cls.vendor_type

    def test_no_is_default_configured_leaves_order_type_empty(self):
        """_default_order_type() only ever returns a type explicitly
        flagged is_default - with nothing configured, a vendor without its
        own type leaves order_type empty rather than falling back to an
        arbitrary one (e.g. by sequence)."""
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor_without_type.id}
        )
        self.assertFalse(order.order_type)

    def test_no_types_for_company_leaves_order_type_empty(self):
        """other_company has no type at all - not the vendor's, not an
        is_default - so it stays empty, same as when the module has never
        been configured."""
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor_without_type.id,
                "company_id": self.other_company.id,
            }
        )
        self.assertFalse(order.order_type)

    def test_default_is_configurable_away_from_sequence_order(self):
        """The default is now a decision, not a side-effect of sequence
        ordering: a type with a higher sequence than another still wins
        once it is the one flagged is_default."""
        lower_sequence_type = self.env["purchase.order.type"].create(
            {
                "name": "POType Lower Sequence",
                "company_id": self.company.id,
                "sequence": 1,
            }
        )
        higher_sequence_default = self.env["purchase.order.type"].create(
            {
                "name": "POType Higher Sequence Default",
                "company_id": self.company.id,
                "sequence": 100,
                "is_default": True,
            }
        )
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor_without_type.id}
        )
        self.assertEqual(order.order_type, higher_sequence_default)
        self.assertNotEqual(order.order_type, lower_sequence_type)

    def test_company_specific_default_wins_over_global_default(self):
        """A global default exists for companies that have none of their
        own - it must not override a company's own default, regardless of
        which one has the lower sequence."""
        global_default = self.env["purchase.order.type"].create(
            {
                "name": "POType Global Default",
                "company_id": False,
                "sequence": 1,
                "is_default": True,
            }
        )
        company_default = self.env["purchase.order.type"].create(
            {
                "name": "POType Company Specific Default",
                "company_id": self.company.id,
                "sequence": 100,
                "is_default": True,
            }
        )
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor_without_type.id}
        )
        self.assertEqual(order.order_type, company_default)
        self.assertNotEqual(order.order_type, global_default)

    def test_default_order_type_used_when_vendor_has_none(self):
        default_type = self.env["purchase.order.type"].create(
            {
                "name": "POType Company Default",
                "company_id": self.company.id,
                "is_default": True,
            }
        )
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor_without_type.id}
        )
        self.assertEqual(order.order_type, default_type)

    def test_vendor_type_wins_over_default_on_create(self):
        self.env["purchase.order.type"].create(
            {
                "name": "POType Company Default 2",
                "company_id": self.company.id,
                "is_default": True,
            }
        )
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor_with_type.id}
        )
        self.assertEqual(order.order_type, self.vendor_type)

    def test_only_one_default_per_company(self):
        self.env["purchase.order.type"].create(
            {
                "name": "POType Default A",
                "company_id": self.company.id,
                "is_default": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["purchase.order.type"].create(
                {
                    "name": "POType Default B",
                    "company_id": self.company.id,
                    "is_default": True,
                }
            )

    def test_one_default_per_different_company_is_allowed(self):
        self.env["purchase.order.type"].create(
            {
                "name": "POType Default Company A",
                "company_id": self.company.id,
                "is_default": True,
            }
        )
        # Must not raise: different company.
        self.env["purchase.order.type"].create(
            {
                "name": "POType Default Company B",
                "company_id": self.other_company.id,
                "is_default": True,
            }
        )

    def test_commercial_partner_fallback_on_create(self):
        parent = self.env["res.partner"].create(
            {"name": "POType Commercial Parent", "is_company": True}
        )
        parent.purchase_type = self.vendor_type
        child = self.env["res.partner"].create(
            {"name": "POType Commercial Child", "parent_id": parent.id}
        )
        self.assertFalse(child.purchase_type)

        order = self.env["purchase.order"].create({"partner_id": child.id})
        self.assertEqual(order.order_type, self.vendor_type)

    def test_payment_term_and_incoterm_follow_order_type_on_create(self):
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor_with_type.id}
        )
        self.assertEqual(order.payment_term_id, self.payterm)
        self.assertEqual(order.incoterm_id, self.incoterm)

    def test_explicit_payment_term_is_not_overridden_on_create(self):
        other_payterm = self.env["account.payment.term"].create(
            {"name": "POType Other Payment Term"}
        )
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor_with_type.id,
                "payment_term_id": other_payterm.id,
            }
        )
        self.assertEqual(order.payment_term_id, other_payterm)
        # order_type itself is still resolved normally.
        self.assertEqual(order.order_type, self.vendor_type)

    def test_explicit_order_type_still_gets_its_payment_term_on_create(self):
        """An order_type given explicitly by a background process must still
        propagate its payment_term_id/incoterm_id - only the *type* lookup
        is skipped when it's already given, not the propagation."""
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor_without_type.id,
                "order_type": self.vendor_type.id,
            }
        )
        self.assertEqual(order.payment_term_id, self.payterm)
        self.assertEqual(order.incoterm_id, self.incoterm)

    def test_onchange_company_prefers_partner_type_over_default(self):
        company_default = self.env["purchase.order.type"].create(
            {
                "name": "POType Generic Default",
                "company_id": self.other_company.id,
                "is_default": True,
            }
        )
        vendor_type_other_company = self.env["purchase.order.type"].create(
            {
                "name": "POType Vendor Type Other Company",
                "company_id": self.other_company.id,
            }
        )
        self.vendor_with_type.purchase_type = vendor_type_other_company

        order = self.env["purchase.order"].new(
            {
                "partner_id": self.vendor_with_type.id,
                "order_type": self.vendor_type.id,
            }
        )
        order.company_id = self.other_company
        order._onchange_company()
        self.assertEqual(order.order_type, vendor_type_other_company)
        self.assertNotEqual(order.order_type, company_default)

    def test_onchange_partner_fills_company_default_when_order_type_empty(self):
        default_type = self.env["purchase.order.type"].create(
            {
                "name": "POType Onchange Default",
                "company_id": self.company.id,
                "is_default": True,
            }
        )
        order = self.env["purchase.order"].new({})
        order.partner_id = self.vendor_without_type
        order.onchange_partner_id()
        self.assertEqual(order.order_type, default_type)

    def test_bulk_create_resolves_each_order_independently(self):
        """create() batches its partner/order-type lookups internally, but
        each vals entry must still resolve on its own merits: a vendor's
        own type, an explicit type, and the company default (with its
        payment term/incoterm) all in the same call."""
        other_vendor_type = self.env["purchase.order.type"].create(
            {
                "name": "POType Bulk Other Vendor Type",
                "company_id": self.company.id,
            }
        )
        other_vendor = self.env["res.partner"].create(
            {"name": "POType Bulk Other Vendor"}
        )
        other_vendor.purchase_type = other_vendor_type
        default_type = self.env["purchase.order.type"].create(
            {
                "name": "POType Bulk Default",
                "company_id": self.company.id,
                "is_default": True,
            }
        )

        orders = self.env["purchase.order"].create(
            [
                {"partner_id": self.vendor_with_type.id},
                {"partner_id": other_vendor.id},
                {"partner_id": self.vendor_without_type.id},
            ]
        )

        (
            order_from_vendor_with_type,
            order_from_other_vendor,
            order_from_default,
        ) = orders
        self.assertEqual(order_from_vendor_with_type.order_type, self.vendor_type)
        self.assertEqual(order_from_vendor_with_type.payment_term_id, self.payterm)
        self.assertEqual(order_from_vendor_with_type.incoterm_id, self.incoterm)
        self.assertEqual(order_from_other_vendor.order_type, other_vendor_type)
        self.assertEqual(order_from_default.order_type, default_type)
