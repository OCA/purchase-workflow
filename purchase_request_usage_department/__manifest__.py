# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request Usage Department",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "version": "12.0.1.0.0",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": [
        "purchase_request_department",
        "purchase_request_product_usage"
    ],
    "data": [
        "views/hr_department_view.xml",
    ],
    "license": 'LGPL-3',
    "installable": True
}
