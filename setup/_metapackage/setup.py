import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-procurement_purchase_no_grouping',
        'odoo11-addon-product_supplierinfo_discount',
        'odoo11-addon-purchase_date_planned_manual',
        'odoo11-addon-purchase_delivery_split_date',
        'odoo11-addon-purchase_discount',
        'odoo11-addon-purchase_exception',
        'odoo11-addon-purchase_landed_cost',
        'odoo11-addon-purchase_line_procurement_group',
        'odoo11-addon-purchase_location_by_line',
        'odoo11-addon-purchase_minimum_amount',
        'odoo11-addon-purchase_open_qty',
        'odoo11-addon-purchase_order_approval_block',
        'odoo11-addon-purchase_order_approved',
        'odoo11-addon-purchase_order_archive',
        'odoo11-addon-purchase_order_line_stock_available',
        'odoo11-addon-purchase_order_secondary_unit',
        'odoo11-addon-purchase_tier_validation',
        'odoo11-addon-stock_landed_cost_company_percentage',
        'odoo11-addon-subcontracted_service',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
