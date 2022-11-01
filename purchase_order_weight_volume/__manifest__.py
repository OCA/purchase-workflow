{
    "name": "Purchase Order Weight and Volume",
    "summary": """Display purchase order weight and volume""",
    "version": "14.0.1.0.0",
    "author": "Ilyas, Ooops404, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
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
