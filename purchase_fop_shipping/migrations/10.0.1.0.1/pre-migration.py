# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from openupgradelib.openupgrade import column_exists, copy_columns


@openupgrade.migrate()
def migrate(env, version):
    if not column_exists(env.cr, 'res_partner', '_tmp_fop_shipping'):
        copy_columns(
            env.cr, {
                'res_partner': [
                    ('fop_shipping', '_tmp_fop_shipping', 'numeric')
                ]
            }
        )
