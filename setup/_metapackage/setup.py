import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-product_form_purchase_link>=15.0dev,<15.1dev',
        'odoo-addon-purchase_discount>=15.0dev,<15.1dev',
        'odoo-addon-purchase_reception_notify>=15.0dev,<15.1dev',
        'odoo-addon-purchase_request>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
