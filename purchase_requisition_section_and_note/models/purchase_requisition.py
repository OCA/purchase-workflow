from odoo import fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    # Split requisition_line_ids in two fields handled thanks to domain
    # Keep original field line_ids to keep all the native functionnalities
    line_ids = fields.One2many(domain=[("display_type", "=", False)])

    line_with_sectionnote_ids = fields.One2many(
        comodel_name="purchase.requisition.line",
        inverse_name="requisition_id",
        string="Requisition Lines With Sections & Notes",
        copy=False,
    )
