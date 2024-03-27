{
    "name": "Purchase Delegation",
    "summary": "Extends the functionality of Purchase Orders to "
    "support a delegationn process.",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Purchases",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Le Filament, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["purchase_order_approved", "base_delegation"],
    "data": ["views/purchase_order_view.xml"],
}
