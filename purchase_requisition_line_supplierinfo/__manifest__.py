# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Requisition Line Supplierinfo",
    "summary": "Lead time and minimum quantity on blanket order lines, "
    "written onto the vendor pricelist line they create",
    "version": "20.0.1.0.0",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["HviorForgeFlow"],
    "license": "AGPL-3",
    "depends": ["purchase_requisition"],
    "data": ["views/purchase_requisition_views.xml"],
    "installable": True,
}
