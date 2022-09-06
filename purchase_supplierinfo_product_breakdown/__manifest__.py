{
    "name": "Purchase Supplierinfo Product Breakdown",
    "summary": "Purchase Supplierinfo Product Breakdown",
    "author": "Ooops, Cetmix, Odoo Community Association (OCA)",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/product_supplierinfo_views.xml",
        "views/product_template_views.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
