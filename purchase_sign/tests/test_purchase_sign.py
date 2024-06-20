# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import binascii
import json
from unittest.mock import patch

from odoo import _
from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserPortal
from odoo.addons.purchase.models.purchase import PurchaseOrder


@tagged("post_install", "-at_install")
class TestPurchaseSign(HttpCaseWithUserPortal):
    def test_01_portal_purchase_signature_tour(self):
        """The goal of this test is to make sure the portal user can sign PO."""
        self.user_portal.company_id.purchase_portal_confirmation_sign = True
        portal_user_partner = self.partner_portal
        # create a PO to be signed
        purchase_order = self.env["purchase.order"].create(
            {
                "name": "test PO",
                "partner_id": portal_user_partner.id,
                "state": "sent",
            }
        )
        self.env["purchase.order.line"].create(
            {
                "order_id": purchase_order.id,
                "product_id": self.env["product.product"]
                .create({"name": "A product"})
                .id,
                "price_unit": 10.0,
            }
        )

        # must be sent to the user so he can see it
        email_act = purchase_order.action_rfq_send()
        email_ctx = email_act.get("context", {})
        purchase_order.with_context(**email_ctx).message_post_with_template(
            email_ctx.get("default_template_id")
        )

        self.start_tour("/", "purchase_signature", login="portal")

    def test_02_portal_purchase_check_errors(self):
        """The goal of this test is to check error handling."""
        self.user_portal.company_id.purchase_portal_confirmation_sign = True
        portal_user_partner = self.partner_portal
        purchase_order = self.env["purchase.order"].create(
            {
                "name": "test PO2",
                "partner_id": portal_user_partner.id,
                "access_token": "test_po",
            }
        )
        self.env["purchase.order.line"].create(
            {
                "order_id": purchase_order.id,
                "product_id": self.env["product.product"]
                .create({"name": "A product"})
                .id,
                "price_unit": 10.0,
            }
        )
        data = json.dumps({}).encode()
        resp = self.url_open(
            "/my/purchase/{}/accept".format(
                purchase_order.id,
            ),
            data=data,
            allow_redirects=False,
            headers={"Content-Type": "application/json"},
        )
        self.assertIn(_("Invalid order."), resp.text)
        resp = self.url_open(
            "/my/purchase/{}/accept?access_token={}".format(
                purchase_order.id, "test_po"
            ),
            data=data,
            allow_redirects=False,
            headers={"Content-Type": "application/json"},
        )
        self.assertIn(
            _("The order is not in a state requiring vendor signature."), resp.text
        )
        purchase_order.state = "sent"
        resp = self.url_open(
            "/my/purchase/{}/accept?access_token={}".format(
                purchase_order.id, "test_po"
            ),
            data=data,
            allow_redirects=False,
            headers={"Content-Type": "application/json"},
        )
        self.assertIn(_("Signature is missing"), resp.text)

        def write(self, vals):
            raise binascii.Error

        with patch.object(
            PurchaseOrder,
            "write",
            write,
        ):
            resp = self.url_open(
                "/my/purchase/{}/accept?access_token={}".format(
                    purchase_order.id, "test_po"
                ),
                data=json.dumps({"params": {"signature": "Joel Willis"}}).encode(),
                allow_redirects=False,
                headers={"Content-Type": "application/json"},
            )
            self.assertIn(_("Invalid signature data"), resp.text)
