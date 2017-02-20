# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate_status(cr):

    cr.execute("""
        UPDATE purchase_request_line SET
        purchase_state = False
        WHERE purchase_state = 'none'
    """)

    cr.execute("""
        UPDATE purchase_request_line SET
        purchase_state = 'purchase'
        WHERE purchase_state = 'confirmed'
    """)


def migrate(cr, version):
    migrate_status(cr)
