# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "purchase_exception", "migrations/12.0.1.0.1/noupdate_changes.xml"
    )
