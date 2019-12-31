import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-product_form_purchase_link',
        'odoo13-addon-purchase_open_qty',
        'odoo13-addon-purchase_order_archive',
        'odoo13-addon-purchase_reception_notify',
        'odoo13-addon-purchase_tier_validation',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
