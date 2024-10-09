# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

# pylint: disable=W8150
from odoo.addons.product_main_seller import pre_init_hook


@openupgrade.migrate()
def migrate(env, version):
    pre_init_hook(env.cr)
