# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Request Sequence Option",
    "summary": "Manage sequence options for purchase.request",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["base_sequence_option", "purchase_request"],
    "data": ["data/purchase_request_sequence_option.xml"],
    "demo": ["demo/purchase_request_demo_options.xml"],
    "development_status": "Alpha",
    "maintainers": ["ps-tubtim"],
    "installable": True,
}
