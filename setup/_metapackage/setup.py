import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-procurement_purchase_no_grouping',
        'odoo9-addon-product_by_supplier',
        'odoo9-addon-product_supplier_code_purchase',
        'odoo9-addon-product_supplierinfo_discount',
        'odoo9-addon-purchase_date_planned_manual',
        'odoo9-addon-purchase_delivery_split_date',
        'odoo9-addon-purchase_discount',
        'odoo9-addon-purchase_fiscal_position_update',
        'odoo9-addon-purchase_location_by_line',
        'odoo9-addon-purchase_open_qty',
        'odoo9-addon-purchase_order_analytic_search',
        'odoo9-addon-purchase_order_approved',
        'odoo9-addon-purchase_order_type',
        'odoo9-addon-purchase_order_variant_mgmt',
        'odoo9-addon-purchase_picking_state',
        'odoo9-addon-purchase_request',
        'odoo9-addon-purchase_request_department',
        'odoo9-addon-purchase_request_procurement',
        'odoo9-addon-purchase_request_to_procurement',
        'odoo9-addon-purchase_request_to_requisition',
        'odoo9-addon-purchase_request_to_rfq',
        'odoo9-addon-purchase_request_to_rfq_order_approved',
        'odoo9-addon-purchase_tier_validation',
        'odoo9-addon-subcontracted_service',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
