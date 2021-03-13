import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-product_form_purchase_link',
        'odoo14-addon-purchase_commercial_partner',
        'odoo14-addon-purchase_delivery_split_date',
        'odoo14-addon-purchase_discount',
        'odoo14-addon-purchase_invoice_plan',
        'odoo14-addon-purchase_last_price_info',
        'odoo14-addon-purchase_location_by_line',
        'odoo14-addon-purchase_manual_currency',
        'odoo14-addon-purchase_open_qty',
        'odoo14-addon-purchase_order_archive',
        'odoo14-addon-purchase_order_line_deep_sort',
        'odoo14-addon-purchase_order_line_menu',
        'odoo14-addon-purchase_order_line_price_history',
        'odoo14-addon-purchase_order_type',
        'odoo14-addon-purchase_order_uninvoiced_amount',
        'odoo14-addon-purchase_reception_status',
        'odoo14-addon-purchase_request',
        'odoo14-addon-purchase_request_tier_validation',
        'odoo14-addon-purchase_requisition_tier_validation',
        'odoo14-addon-purchase_tier_validation',
        'odoo14-addon-purchase_work_acceptance',
        'odoo14-addon-purchase_work_acceptance_invoice_plan',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
