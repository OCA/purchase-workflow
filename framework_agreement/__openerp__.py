# -*- coding: utf-8 -*-
#    Author: Nicolas Bessi, Leonardo Pistone
#    Copyright 2013-2015 Camptocamp SA
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
{'name': 'Framework Agreement',
 'summary': 'Long Term Agreement (or Framework Agreement) for purchases',
 'version': '8.0.2.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Purchase Management',
 'complexity': 'normal',
 'depends': ['stock', 'procurement', 'purchase', 'web_context_tunnel'],
 'website': 'http://www.camptocamp.com',
 'data': ['data.xml',
          'view/product_view.xml',
          'view/framework_agreement_view.xml',
          'view/portfolio.xml',
          'view/purchase_view.xml',
          'view/company_view.xml',
          'security/multicompany.xml',
          'security/groups.xml',
          'security/ir.model.access.csv'],
 'demo': [],
 'test': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 }
