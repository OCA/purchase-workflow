# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import pycompat

import logging
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """email from in templates will be `user_id` now."""
    _logger.info("Update RFQ/PO email templates")
    cr.execute("""
        SELECT id, email_from
        FROM mail_template
        WHERE model = 'purchase.order';
    """)
    for template_id, email_from in cr.fetchall():
        new_mail_from = pycompat.to_text(email_from.replace("create_uid", "user_id"))
        cr.execute("""
            UPDATE mail_template
            SET email_from = %s
            WHERE id = %s;
        """, (new_mail_from, template_id))


def uninstall_hook(cr, registry):
    """set back email from to create_uid"""
    _logger.info("Update RFQ/PO email templates")
    cr.execute("""
        SELECT id, email_from
        FROM mail_template
        WHERE model = 'purchase.order';
    """)
    for template_id, email_from in cr.fetchall():
        new_mail_from = pycompat.to_text(email_from.replace("user_id", "create_uid"))
        cr.execute("""
            UPDATE mail_template
            SET email_from = %s
            WHERE id = %s;
        """, (new_mail_from, template_id))
