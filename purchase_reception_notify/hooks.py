# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Existing employees should be subscribed to the new subtype for all
    existing purchase orders..
    """
    _logger.info(
        "Starting task to update internal followers for "
        "existing purchase orders to assign the new subtype "
        "Purchase Receptions."
    )
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        users = env["res.users"].search([])
        followers = env["mail.followers"].search(
            [
                ("res_model", "=", "purchase.order"),
                ("partner_id", "in", users.mapped("partner_id").ids),
            ]
        )
        for follower in followers:
            follower.subtype_ids += env.ref(
                "purchase_reception_notify.mt_purchase_reception"
            )
    _logger.info(
        "Finalized task to update internal followers for "
        "existing purchase orders to assign the new subtype "
        "Purchase Receptions."
    )
