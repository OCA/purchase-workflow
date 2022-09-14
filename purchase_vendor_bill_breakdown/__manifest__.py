{
    "name": "Purchase Vendor Bill Breakdown",
    "summary": "Purchase Vendor Bill Breakdown",
    "author": "Ooops, Cetmix, Odoo Community Association (OCA)",
    "version": "14.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "maintainers": ["geomer198", "CetmixGitDrone"],
    "depends": ["purchase_supplierinfo_product_breakdown"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_supplierinfo_views.xml",
        "views/product_template_view.xml",
        "views/purchase_order_views.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
