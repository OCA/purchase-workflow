# Copyright 2017-2020 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Loaded after installing the module."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        purchase_requests = env["purchase.request"].search([])
        _logger.info(
            "Adding the department to %d purchase requests", len(purchase_requests)
        )
        for purchase_request in purchase_requests:
            purchase_request.onchange_requested_by()
