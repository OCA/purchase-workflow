# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Invoice Plan Allocation",
    "summary": "Allocate each purchase invoice plan to specific purchase order lines",
    "version": "18.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "depends": ["purchase_invoice_plan"],
    "data": [
        "security/purchase_invoice_plan_allocation_security.xml",
        "security/ir.model.access.csv",
        "views/purchase_invoice_plan_views.xml",
        "views/purchase_order_views.xml",
        "wizard/purchase_create_invoice_plan_view.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Alpha",
    "maintainers": ["Saran440"],
    "installable": True,
}
