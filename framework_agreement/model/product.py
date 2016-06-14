# -*- coding: utf-8 -*-
# © 2013-2015 Camptocamp SA - Nicolas Bessi, Leonardo Pistone
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductProduct(models.Model):
    """Add relation to framework agreement"""

    _inherit = "product.product"
    framework_agreement_ids = fields.One2many(
        comodel_name='framework.agreement',
        inverse_name='product_id',
        string='Framework Agreements (LTA)',
        copy=False,
    )
