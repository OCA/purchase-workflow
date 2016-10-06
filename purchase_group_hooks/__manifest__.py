# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
{'name': 'Add hooks to the merge PO feature.',
 'version': '0.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Purchase Management',
 'complexity': "normal",
 'depends': ['purchase'],
 'description': """
 In the core OpenERP purchase module, there is a wizard to merge purchase
 orders. That feature is convenient, but as soon as a field is added to the
 purchase order, it does not work anymore and needs to be patched.
 The original implementation does not provide any hooks for extension, and
 modules can only reimplement a method completely. This required a lot of copy
 and paste, and worse, it breaks if two modules attempt to do that.

 Therefore, this module reimplements the feature, with the same basic result
 in the standard case. Hooks are provided for extra modules that add fields
 or change the logic.
 """,
 'website': 'http://www.camptocamp.com/',
 'data': [],
 'installable': False,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 'test': ['test/merge_order.yml'],
 }
