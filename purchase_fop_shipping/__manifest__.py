# © 2017 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Free-Of-Paiment shipping",
    "version": "13.0.1.0.0",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "maintainer": "Akretion",
    "license": "AGPL-3",
    "category": "Purchase",
    "depends": ["purchase"],
    "data": [
        "security/res_groups.xml",
        "views/purchase_order.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
}
