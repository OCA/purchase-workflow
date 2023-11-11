# © 2016 Chafique DELLI @ Akretion
# © 2017 Today Mourad EL HADJ MIMOUNE @ Akretion
# 2020 Manuel Calero - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase and Invoice Allowed Product",
    "summary": "This module allows to select only products that can be "
    "supplied by the vendor",
    "version": "16.0.2.0.1",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/purchase-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["purchase", "base_view_inheritance_extension"],
    "data": [
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
}
