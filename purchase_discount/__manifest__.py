# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2014-2017 Tecnativa - Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase order lines with discounts",
    "author": "Tiny, "
    "Acysos S.L., "
    "Tecnativa, "
    "ACSONE SA/NV,"
    "GRAP,"
    "Odoo Community Association (OCA)",
    "version": "13.0.1.0.4",
    "category": "Purchase Management",
    "website": "https://github.com/OCA/purchase-workflow",
    "depends": ["purchase_stock"],
    "data": [
        "views/purchase_discount_view.xml",
        "views/report_purchaseorder.xml",
        "views/product_supplierinfo_view.xml",
        "views/res_partner_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "images": ["images/purchase_discount.png"],
}
