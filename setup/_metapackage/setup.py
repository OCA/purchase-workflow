import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-procurement_purchase_no_grouping',
        'odoo12-addon-purchase_delivery_split_date',
        'odoo12-addon-purchase_exception',
        'odoo12-addon-purchase_force_invoiced',
        'odoo12-addon-purchase_line_procurement_group',
        'odoo12-addon-purchase_open_qty',
        'odoo12-addon-purchase_order_approved',
        'odoo12-addon-purchase_order_archive',
        'odoo12-addon-purchase_product_usage',
        'odoo12-addon-purchase_tier_validation',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
