# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
from openerp import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Loaded after installing the module."""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        purchase_requests = env['purchase.request'].search([])
        _logger.info(
            "Adding the department to %d purchase requests",
            len(purchase_requests))
        for purchase_request in purchase_requests:
            purchase_request.onchange_requested_by()
