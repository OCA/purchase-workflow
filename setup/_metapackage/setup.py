import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-purchase_advance_payment>=16.0dev,<16.1dev',
        'odoo-addon-purchase_all_shipments>=16.0dev,<16.1dev',
        'odoo-addon-purchase_allowed_product>=16.0dev,<16.1dev',
        'odoo-addon-purchase_commercial_partner>=16.0dev,<16.1dev',
        'odoo-addon-purchase_default_terms_conditions>=16.0dev,<16.1dev',
        'odoo-addon-purchase_delivery_split_date>=16.0dev,<16.1dev',
        'odoo-addon-purchase_discount>=16.0dev,<16.1dev',
        'odoo-addon-purchase_exception>=16.0dev,<16.1dev',
        'odoo-addon-purchase_force_invoiced>=16.0dev,<16.1dev',
        'odoo-addon-purchase_last_price_info>=16.0dev,<16.1dev',
        'odoo-addon-purchase_line_procurement_group>=16.0dev,<16.1dev',
        'odoo-addon-purchase_lot>=16.0dev,<16.1dev',
        'odoo-addon-purchase_merge>=16.0dev,<16.1dev',
        'odoo-addon-purchase_no_rfq>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_approved>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_line_menu>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_no_zero_price>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_owner>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_product_recommendation>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_supplierinfo_update>=16.0dev,<16.1dev',
        'odoo-addon-purchase_order_uninvoiced_amount>=16.0dev,<16.1dev',
        'odoo-addon-purchase_request>=16.0dev,<16.1dev',
        'odoo-addon-purchase_request_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-purchase_requisition_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-purchase_stock_packaging>=16.0dev,<16.1dev',
        'odoo-addon-purchase_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-purchase_triple_discount>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
