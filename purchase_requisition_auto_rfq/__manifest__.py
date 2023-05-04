# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Purchase Requisition Auto RFQ",
    "summary": "Automatically create RFQs from a purchase requisition",
    "version": "14.0.1.1.0",
    "author": "Camptocamp, Métal Sartigan, Odoo Community Association (OCA)",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": [
        "purchase_requisition",
    ],
    "demo": [
        "demo/product_product.xml",
    ],
    "data": [
        "view/purchase_requisition.xml",
    ],
    "installable": True,
}
