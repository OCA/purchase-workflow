# Copyright 2024 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import binascii

from odoo import _, fields, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalPurchase(CustomerPortal):
    def _purchase_order_get_page_view_values(self, order, access_token, **kwargs):
        response = super(PortalPurchase, self)._purchase_order_get_page_view_values(
            order=order, access_token=access_token, **kwargs
        )
        if kwargs.get("message"):
            response.update({"message": kwargs.get("message")})
        return response

    @http.route(
        ["/my/purchase/<int:order_id>/accept"], type="json", auth="public", website=True
    )
    def portal_purchase_accept(
        self, order_id, access_token=None, name=None, signature=None
    ):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get("access_token")
        try:
            order_sudo = self._document_check_access(
                "purchase.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return {"error": _("Invalid order.")}

        if not order_sudo._has_to_be_signed():
            return {
                "error": _("The order is not in a state requiring vendor signature.")
            }
        if not signature:
            return {"error": _("Signature is missing.")}

        try:
            order_sudo.write(
                {
                    "signed_by": name,
                    "signed_on": fields.Datetime.now(),
                    "signature": signature,
                }
            )
        except (TypeError, binascii.Error):
            return {"error": _("Invalid signature data.")}
        order_sudo.button_confirm()
        pdf = (
            request.env["ir.actions.report"]
            .sudo()
            ._render_qweb_pdf("purchase.action_report_purchase_order", [order_sudo.id])[
                0
            ]
        )

        _message_post_helper(
            "purchase.order",
            order_sudo.id,
            _("Order signed by %s", name),
            attachments=[("%s.pdf" % order_sudo.name, pdf)],
            token=access_token,
        )

        query_string = "&message=sign_ok"
        return {
            "force_refresh": True,
            "redirect_url": order_sudo.get_portal_url(query_string=query_string),
        }
