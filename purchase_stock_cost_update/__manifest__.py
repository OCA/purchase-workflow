# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
{
    "name": "Update costs from purchase",
    "summary": "Allows to update valuation layers once the purchase is received",
    "version": "16.0.1.0.1",
    "category": "Purchase Management",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu", "rafaelbn"],
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "LGPL-3",
    "depends": ["purchase_stock"],
    "data": [
        "views/purchase_order_form_views.xml",
        "views/stock_valuation_layer_views.xml",
    ],
}
