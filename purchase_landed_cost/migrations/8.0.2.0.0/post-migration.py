# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE purchase_cost_distribution_expense AS exp
        SET invoice_id = il.invoice_id
        FROM account_invoice_line AS il
        WHERE exp.invoice_id is NULL
        AND exp.invoice_line = il.id""")
