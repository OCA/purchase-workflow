import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-procurement_purchase_no_grouping',
        'odoo12-addon-product_form_purchase_link',
        'odoo12-addon-purchase_commercial_partner',
        'odoo12-addon-purchase_date_planned_manual',
        'odoo12-addon-purchase_delivery_split_date',
        'odoo12-addon-purchase_deposit',
        'odoo12-addon-purchase_discount',
        'odoo12-addon-purchase_exception',
        'odoo12-addon-purchase_force_invoiced',
        'odoo12-addon-purchase_invoice_plan',
        'odoo12-addon-purchase_landed_cost',
        'odoo12-addon-purchase_last_price_info',
        'odoo12-addon-purchase_line_procurement_group',
        'odoo12-addon-purchase_location_by_line',
        'odoo12-addon-purchase_open_qty',
        'odoo12-addon-purchase_order_approved',
        'odoo12-addon-purchase_order_archive',
        'odoo12-addon-purchase_order_line_deep_sort',
        'odoo12-addon-purchase_order_line_description',
        'odoo12-addon-purchase_product_usage',
        'odoo12-addon-purchase_quick',
        'odoo12-addon-purchase_reception_notify',
        'odoo12-addon-purchase_request',
        'odoo12-addon-purchase_request_department',
        'odoo12-addon-purchase_request_product_usage',
        'odoo12-addon-purchase_request_tier_validation',
        'odoo12-addon-purchase_request_usage_department',
        'odoo12-addon-purchase_requisition_tier_validation',
        'odoo12-addon-purchase_tier_validation',
        'odoo12-addon-purchase_triple_discount',
        'odoo12-addon-subcontracted_service',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
