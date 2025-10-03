from odoo import fields, models


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    # Returns mandatory for classic line thanks to _sql_constraints and view
    product_id = fields.Many2one(required=False)

    # New fields to handle section & note
    name = fields.Text()
    sequence = fields.Integer()

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    _sql_constraints = [
        (
            "bom_required_fields_product_qty",
            "CHECK(display_type IS NOT NULL OR"
            "(product_id IS NOT NULL AND product_qty IS NOT NULL))",
            "Missing required fields on purchase requisition: product and quantity.",
        ),
    ]
