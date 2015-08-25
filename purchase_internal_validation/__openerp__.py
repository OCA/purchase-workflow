# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name" : "Internal Validation for Purchase",
    "version" : "1.1",
    "category": 'Purchases',
    "depends" : [
        "base",
        "purchase",
    ],
    "author" : 'Savoir-faire Linux',
    "description": """
        This module modifies the purchase workflow in order to validate purchases 
        that exceeds minimum amount set by configuration wizard.
    """,
    'website': 'http://www.savoirfairelinux.com',
    'data': [
        'purchase_internal_validation_workflow.xml',
        'purchase_internal_validation_installer.xml',
        'purchase_view.xml'
    ],
    'demo': [],
    'installable': True,
    'active': False,
    'certificate' : '',

}
