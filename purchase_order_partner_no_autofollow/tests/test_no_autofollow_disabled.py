from odoo.tests import Form, tagged

from .common import NoAutofollowCommon


@tagged("post_install", "-at_install", "standart")
class TestPurchaseOrderNoAutofollow(NoAutofollowCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.env["ir.config_parameter"].sudo().set_param(
            "purchase_order_partner_no_autofollow.partner_disable_autofollow", True
        )

        with Form(self.env["purchase.order"]) as form:
            form.partner_id = self.partner1
            form.order_type = self.order_type
            with form.order_line.new() as line_1:
                line_1.product_id = self.product1
            self.purchase_order_1 = form.save()

    def test_partner_disable_autofollow(self):
        """
        'Vendor no autofollow' mode is enabled in settings.
        Test whether the option to disable autofollow is enabled
        or disabled
        """
        self.assertEqual(
            self.purchase_order_1._partner_disable_autofollow(),
            "True",
            "Must be equal to True",
        )

    def test_message_subscribe_1(self):
        """'Vendor no autofollow' mode is enabled in settings.
        Test whether the user will be added to the autofollow
        """
        self.purchase_order_1.with_context(
            purchase_partner_disable_autofollow=self.purchase_order_1._partner_disable_autofollow()
        ).message_subscribe(partner_ids=[self.partner1.id])
        self.assertNotIn(
            self.purchase_order_1.partner_id.id,
            self.purchase_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_message_subscribe_2(self):
        """'Vendor no autofollow' mode is enabled in settings.
        Test whether the user will be added to the autofollow
        """
        self.purchase_order_1.with_context(
            purchase_partner_disable_autofollow=self.purchase_order_1._partner_disable_autofollow()
        ).message_subscribe(partner_ids=[])
        self.assertNotIn(
            self.purchase_order_1.partner_id.id,
            self.purchase_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_message_subscribe_3(self):
        """'Vendor no autofollow' mode is enabled in settings.
        Test whether the user will be added to the autofollow
        """
        self.purchase_order_1.with_context(
            purchase_partner_disable_autofollow=self.purchase_order_1._partner_disable_autofollow()
        ).message_subscribe()
        self.assertNotIn(
            self.purchase_order_1.partner_id.id,
            self.purchase_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_purchase_order_create(self):
        """
        'Vendor no autofollow' mode is enabled in settings.
        Test if there is a client among subscribers when creating
        a record
        """
        self.assertNotIn(
            self.purchase_order_1.partner_id.id,
            self.purchase_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )

    def test_purchase_order_button_confirm(self):
        """
        'Vendor no autofollow' mode is enabled in settings.
        Test if there is a customer among the subscribers
        after confirming the order.
        """
        self.purchase_order_1.button_confirm()

        self.assertNotIn(
            self.purchase_order_1.partner_id.id,
            self.purchase_order_1.message_follower_ids.mapped("partner_id").ids,
            msg="The customer must not be among the subscribers",
        )
