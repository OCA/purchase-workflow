# -*- coding: utf-8 -*-
# Copyright 2015 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Purchase order line description",
    'version': '10.0.1.0.0',
    'category': 'Purchase Management',
    'author': "Agile Business Group, Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'purchase',
    ],
    "data": [
        'security/res_groups_security.xml',
        'views/purchase_config_settings_view.xml',
    ],
    "installable": True
}
