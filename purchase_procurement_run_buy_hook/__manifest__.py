# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Purchase Procurement Run Buy Hook",
    "summary": "Hook to allow extensions to _run_buy method in "
               "procurement.rule",
    "version": "11.0.1.0.0",
    "license": "LGPL-3",
    "website": "https://github.com/purchase-workflow",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Purchase Management",
    "depends": [
        "purchase",
    ],
    "post_load": "post_load_hook",
    "installable": True,
}
