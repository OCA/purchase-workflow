import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-purchase_advance_payment>=16.0dev,<16.1dev',
        'odoo-addon-purchase_allowed_product>=16.0dev,<16.1dev',
        'odoo-addon-purchase_commercial_partner>=16.0dev,<16.1dev',
        'odoo-addon-purchase_delivery_split_date>=16.0dev,<16.1dev',
        'odoo-addon-purchase_discount>=16.0dev,<16.1dev',
        'odoo-addon-purchase_force_invoiced>=16.0dev,<16.1dev',
        'odoo-addon-purchase_last_price_info>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_approved>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_line_menu>=16.0dev,<16.1dev',
        'odoo-addon-purchase_request>=16.0dev,<16.1dev',
        'odoo-addon-purchase_request_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-purchase_requisition_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-purchase_stock_packaging>=16.0dev,<16.1dev',
        'odoo-addon-purchase_tier_validation>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
