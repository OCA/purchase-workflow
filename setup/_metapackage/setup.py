import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-purchase_commercial_partner',
        'odoo14-addon-purchase_last_price_info',
        'odoo14-addon-purchase_open_qty',
        'odoo14-addon-purchase_order_archive',
        'odoo14-addon-purchase_request',
        'odoo14-addon-purchase_request_tier_validation',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
