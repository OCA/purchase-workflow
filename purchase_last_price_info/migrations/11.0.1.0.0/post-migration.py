# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from odoo.addons.purchase_last_price_info import set_last_price_info


@openupgrade.migrate()
def migrate(env, version):
    set_last_price_info(env.cr, env.registry)
