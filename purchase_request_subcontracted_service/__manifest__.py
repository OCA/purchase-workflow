# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).
{
    "name": "Purchase Request Subcontracted Service",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA)",
    "version": "11.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "summary": "Glue module to purchase request on services.",
    "category": "Purchase Management",
    "depends": [
        "purchase_request",
        "product"
    ],
    "data": [
        "views/product_template.xml",
    ],
    "license": 'LGPL-3',
    'installable': True,
    'auto_install': True,
}
