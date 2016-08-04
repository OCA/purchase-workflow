# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Product Supplierinfo Tender",
    "summary": "Introduces a Tendering Process for Supplier Price agreements",
    "version": "9.0.1.1.0",
    "category": "Generic Modules",
    "author": "Eficent Business and IT Consulting Services S.L.",
    "website": "https://www.odoo-community.org",
    "license": "LGPL-3",
    "depends": ['purchase',
                'product_supplierinfo_editable',
                'product_supplierinfo_state'
                ],
    "data": [
        'security/ir.model.access.csv',
        'security/product_supplierinfo_tender_security.xml',
        'data/product_supplierinfo_tender_sequence.xml',
        'data/product_supplierinfo_bid_sequence.xml',
        'wizards/product_supplierinfo_tender_create_bid_view.xml',
        'views/product_supplierinfo_bid_view.xml',
        'views/product_supplierinfo_tender_view.xml',
        'views/product_supplierinfo_view.xml',
        'views/report_pricelist_bid.xml',
        'views/report_pricelist_tender.xml',
        'pricelist_report.xml',
    ],
    "installable": True,
}

