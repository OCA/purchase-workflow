# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Procurement Batch Generator',
    'version': '9.0.1.0.0',
    'category': 'Warehouse Management',
    'license': 'AGPL-3',
    'summary': 'Wizard to create procurements from product variants',
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['stock'],
    'data': ['wizards/procurement_batch_generator_view.xml'],
    'test': ['test/procurement_batch_generator.yml'],
    'installable': True,
}
