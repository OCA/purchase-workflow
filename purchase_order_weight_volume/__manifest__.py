# Copyright 2023 ooops404
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase Order Weight and Volume",
    "summary": """Display purchase order weight and volume""",
    "version": "16.0.2.0.0",
    "author": "Ilyas, Ooops404, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "maintainers": ["ilyasProgrammer"],
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_order_view.xml",
        "views/res_config_settings_views.xml",
        "report/purchase_report_templates.xml",
    ],
    "installable": True,
}
