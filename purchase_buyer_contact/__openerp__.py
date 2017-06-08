# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Purchase Buyer Contact',
    'version': '9.0.0.0.0',
    'category': 'Purchase',
    'summary': "Store information about your company's buyer",
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
    ],
    'data': [
        'views/view_res_partner.xml',
        'views/view_res_company.xml',
        'views/report_purchasequotation.xml',
        'views/report_purchaseorder.xml',
    ],
    'installable': True,
}
