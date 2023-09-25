# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Work Acceptance Sequence Option",
    "summary": "Manage sequence options for work.acceptance",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase Management",
    "depends": ["base_sequence_option", "purchase_work_acceptance"],
    "data": ["data/purchase_work_acceptance_sequence_option.xml"],
    "demo": ["demo/purchase_work_acceptance_demo_options.xml"],
    "development_status": "Alpha",
    "maintainers": ["ps-tubtim"],
    "installable": True,
}
