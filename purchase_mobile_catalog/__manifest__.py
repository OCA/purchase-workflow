# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Mobile Catalog",
    "summary": "Show 'Catalog' action in mobile view for purchase order lines.",
    "version": "18.0.1.0.0",
    "author": "Binhex, Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase", "product"],
    "data": ["views/purchase_mobile_catalog_views.xml"],
    "installable": True,
    "license": "AGPL-3",
}
