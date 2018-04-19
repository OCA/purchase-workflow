import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-purchase_discount',
        'odoo11-addon-purchase_exception',
        'odoo11-addon-purchase_minimum_amount',
        'odoo11-addon-purchase_order_approval_block',
        'odoo11-addon-stock_landed_cost_company_percentage',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
