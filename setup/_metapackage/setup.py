import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-purchase-workflow",
    description="Meta package for oca-purchase-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-framework_agreement',
        'odoo8-addon-procurement_batch_generator',
        'odoo8-addon-product_by_supplier',
        'odoo8-addon-product_supplierinfo_discount',
        'odoo8-addon-purchase_add_product_supplierinfo',
        'odoo8-addon-purchase_all_shipments',
        'odoo8-addon-purchase_commercial_partner',
        'odoo8-addon-purchase_delivery_address',
        'odoo8-addon-purchase_delivery_split_date',
        'odoo8-addon-purchase_discount',
        'odoo8-addon-purchase_fiscal_position_update',
        'odoo8-addon-purchase_last_price_info',
        'odoo8-addon-purchase_order_line_description',
        'odoo8-addon-purchase_order_reorder_lines',
        'odoo8-addon-purchase_order_revision',
        'odoo8-addon-purchase_order_type',
        'odoo8-addon-purchase_origin_address',
        'odoo8-addon-purchase_partial_invoicing',
        'odoo8-addon-purchase_partner_invoice_method',
        'odoo8-addon-purchase_picking_state',
        'odoo8-addon-purchase_request',
        'odoo8-addon-purchase_request_procurement',
        'odoo8-addon-purchase_request_to_requisition',
        'odoo8-addon-purchase_request_to_rfq',
        'odoo8-addon-purchase_requisition_auto_rfq',
        'odoo8-addon-purchase_requisition_auto_rfq_bid_selection',
        'odoo8-addon-purchase_requisition_bid_selection',
        'odoo8-addon-purchase_requisition_delivery_address',
        'odoo8-addon-purchase_requisition_multicurrency',
        'odoo8-addon-purchase_requisition_transport_document',
        'odoo8-addon-purchase_requisition_type',
        'odoo8-addon-purchase_rfq_bid_workflow',
        'odoo8-addon-purchase_rfq_number',
        'odoo8-addon-purchase_supplier_rounding_method',
        'odoo8-addon-purchase_transport_document',
        'odoo8-addon-quick_purchase',
        'odoo8-addon-vendor_consignment_stock',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
