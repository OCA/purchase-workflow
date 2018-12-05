# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_request = fields.Boolean(
        string='Purchase Request',
        help="Check this box to generate purchase request instead of "
             "generating requests for quotation from procurement."
    )
