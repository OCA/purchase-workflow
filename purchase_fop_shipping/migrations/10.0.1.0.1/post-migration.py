# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_to_company_dependent(
        env,
        'res.partner',
        '_tmp_fop_shipping',
        'fop_shipping',
    )
    openupgrade.drop_columns(
        env.cr,
        [
            ('res_partner', '_tmp_fop_shipping'),
        ]
    )
