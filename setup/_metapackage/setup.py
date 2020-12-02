import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-procurement_purchase_no_grouping',
        'odoo13-addon-product_form_purchase_link',
        'odoo13-addon-purchase_blanket_order',
        'odoo13-addon-purchase_commercial_partner',
        'odoo13-addon-purchase_delivery_split_date',
        'odoo13-addon-purchase_deposit',
        'odoo13-addon-purchase_discount',
        'odoo13-addon-purchase_invoice_plan',
        'odoo13-addon-purchase_isolated_rfq',
        'odoo13-addon-purchase_last_price_info',
        'odoo13-addon-purchase_location_by_line',
        'odoo13-addon-purchase_manual_currency',
        'odoo13-addon-purchase_open_qty',
        'odoo13-addon-purchase_order_approved',
        'odoo13-addon-purchase_order_archive',
        'odoo13-addon-purchase_order_line_deep_sort',
        'odoo13-addon-purchase_order_line_packaging_qty',
        'odoo13-addon-purchase_order_line_price_history',
        'odoo13-addon-purchase_order_line_price_history_discount',
        'odoo13-addon-purchase_order_product_recommendation',
        'odoo13-addon-purchase_order_secondary_unit',
        'odoo13-addon-purchase_order_uninvoiced_amount',
        'odoo13-addon-purchase_product_usage',
        'odoo13-addon-purchase_reception_notify',
        'odoo13-addon-purchase_reception_status',
        'odoo13-addon-purchase_request',
        'odoo13-addon-purchase_request_department',
        'odoo13-addon-purchase_request_tier_validation',
        'odoo13-addon-purchase_requisition_tier_validation',
        'odoo13-addon-purchase_security',
        'odoo13-addon-purchase_tier_validation',
        'odoo13-addon-purchase_warn_message',
        'odoo13-addon-purchase_work_acceptance',
        'odoo13-addon-supplier_calendar',
        'odoo13-addon-vendor_transport_lead_time',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
