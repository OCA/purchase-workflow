# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase order revisions",
    "summary": "Keep track of revised quotations",
    "version": "15.0.0.0.1",
    "category": "Purchase",
    "author": "Open Source Integrators," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "license": "AGPL-3",
    "depends": ["base_revision", "purchase"],
    "data": ["view/purchase_order.xml"],
    "installable": True,
    "post_init_hook": "populate_unrevisioned_name",
}
