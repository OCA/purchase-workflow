# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Transport Mode",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "summary": "Purchase expection based on constraints",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Purchase",
    "depends": [
        "purchase",
        "purchase_exception",
    ],
    "website": "https://github.com/OCA/purchase-workflow",
    "data": [
        "security/ir.model.access.csv",
        "templates/purchase_order_transport_mode_status.xml",
        "views/res_partner_views.xml",
        "views/purchase_transport_mode_views.xml",
        "views/purchase_transport_mode_constraint_views.xml",
        "views/purchase_order_view.xml",
        "views/res_config_settings_views.xml",
        "data/purchase_exception_data.xml",
    ],
    "installable": True,
}
