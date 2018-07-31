import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-procurement_purchase_no_grouping',
        'odoo10-addon-product_by_supplier',
        'odoo10-addon-product_supplier_code_purchase',
        'odoo10-addon-product_supplierinfo_discount',
        'odoo10-addon-purchase_allowed_product',
        'odoo10-addon-purchase_cancel_reason',
        'odoo10-addon-purchase_commercial_partner',
        'odoo10-addon-purchase_delivery_split_date',
        'odoo10-addon-purchase_discount',
        'odoo10-addon-purchase_fiscal_position_update',
        'odoo10-addon-purchase_fop_shipping',
        'odoo10-addon-purchase_line_product_image',
        'odoo10-addon-purchase_location_by_line',
        'odoo10-addon-purchase_minimum_amount',
        'odoo10-addon-purchase_open_qty',
        'odoo10-addon-purchase_order_analytic_search',
        'odoo10-addon-purchase_order_approval_block',
        'odoo10-addon-purchase_order_approved',
        'odoo10-addon-purchase_order_line_description',
        'odoo10-addon-purchase_order_line_sequence',
        'odoo10-addon-purchase_order_revision',
        'odoo10-addon-purchase_picking_state',
        'odoo10-addon-purchase_request',
        'odoo10-addon-purchase_request_procurement',
        'odoo10-addon-purchase_request_to_procurement',
        'odoo10-addon-purchase_request_to_rfq',
        'odoo10-addon-purchase_request_to_rfq_order_approved',
        'odoo10-addon-purchase_triple_discount',
        'odoo10-addon-subcontracted_service',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
