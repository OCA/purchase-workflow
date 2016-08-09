# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3


def migrate(cr, version):
    """Force the computation of the field dropping the column."""
    if not version:
        return
    cr.execute("""
        ALTER TABLE purchase_cost_distribution_expense
        DROP COLUMN display_name
        """)
