# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    purchase_requisition_group_id = fields.Many2one(
        comodel_name='purchase.requisition.type',
        string='Purchase Requisition Grouped',
        ondelete='restrict',
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_requisition_group_id = fields.Many2one(
        comodel_name='purchase.requisition.type',
        string='Purchase Requisition Grouped',
        ondelete='restrict',
    )
