# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Savoir-faire Linux (<http://savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Internal Validation for Purchase",
    "version": "8.0.1.0.0",
    "category": "Purchases",
    "depends": [
        "purchase",
    ],
    "author": "Savoir-faire Linux, Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "data": [
        "data/ir_config_parameter.xml",
        "security/groups.xml",
        "views/res_config.xml",
        "views/purchase.xml",
        "workflow/purchase.xml",
    ],
    "images": [
        "static/description/img/purchase_internal_validation01.png",
    ],
    "installable": True,
}
