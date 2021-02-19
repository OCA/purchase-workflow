# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade
from psycopg2 import sql


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
            UPDATE purchase_cost_distribution_expense pcde
            SET invoice_line = aml.id
            FROM account_move_line aml
            WHERE aml.old_invoice_line_id = pcde.{}"""
        ).format(sql.Identifier(openupgrade.get_legacy_name("invoice_line")),),
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
            UPDATE purchase_cost_distribution_expense pcde
            SET invoice_id = am.id
            FROM account_move am
            WHERE am.old_invoice_id = pcde.{}"""
        ).format(sql.Identifier(openupgrade.get_legacy_name("invoice_id")),),
    )
