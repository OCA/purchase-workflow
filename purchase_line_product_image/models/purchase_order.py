# Copyright 2017 Lucky Kurniawan <kurniawanluckyy@gmail.com>
# Copyright 2026 TesseraTech Solutions S.L. <https://www.tesseratech.es>
# Copyright 2026 Paco Montés <f.montesdoria@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_image = fields.Binary(
        related="product_id.product_tmpl_id.image_1920",
        readonly=True,
    )
