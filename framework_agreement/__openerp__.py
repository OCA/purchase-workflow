# -*- coding: utf-8 -*-
# © 2013-2015 Camptocamp SA - Nicolas Bessi, Leonardo Pistone
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{'name': 'Framework Agreement',
 'summary': 'Long Term Agreement (or Framework Agreement) for purchases',
 'version': '9.0.2.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Purchase Management',
 'complexity': 'normal',
 'depends': ['stock', 'procurement', 'purchase'],
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
