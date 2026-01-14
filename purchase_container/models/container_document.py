from odoo import api, fields, models


class ContainerDocumentType(models.Model):
    """Types of documents required for container shipments."""

    _name = "container.document.type"
    _description = "Container Document Type"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    required = fields.Boolean(
        default=False,
        help="If checked, this document type is required for all containers",
    )
    active = fields.Boolean(default=True)
    description = fields.Text(help="Description or instructions for this document type")


class ContainerDocument(models.Model):
    """Track shipping documents attached to containers."""

    _name = "container.document"
    _description = "Container Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "container_id, document_type_id"

    container_id = fields.Many2one(
        "purchase.container",
        string="Container",
        required=True,
        ondelete="cascade",
        index=True,
    )
    document_type_id = fields.Many2one(
        "container.document.type",
        string="Document Type",
        required=True,
        ondelete="restrict",
    )
    name = fields.Char(compute="_compute_name", store=True)
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment",
        help="The uploaded document file",
    )
    filename = fields.Char(related="attachment_id.name", string="Filename")
    state = fields.Selection(
        [
            ("missing", "Missing"),
            ("pending", "Pending Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="missing",
        required=True,
        tracking=True,
    )
    reference = fields.Char(
        help="External reference number for this document (e.g., invoice number)"
    )
    date_received = fields.Date()
    date_approved = fields.Date()
    notes = fields.Text()
    required = fields.Boolean(
        related="document_type_id.required", string="Required", store=True
    )

    @api.depends("container_id.code", "document_type_id.name")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.container_id.code} - {record.document_type_id.name}"

    @api.onchange("attachment_id")
    def _onchange_attachment_id(self):
        """Auto-update state when attachment is added."""
        if self.attachment_id and self.state == "missing":
            self.state = "pending"
            self.date_received = fields.Date.today()

    def action_approve(self):
        """Approve the document."""
        self.write({"state": "approved", "date_approved": fields.Date.today()})

    def action_reject(self):
        """Reject the document."""
        self.write({"state": "rejected"})

    def action_reset(self):
        """Reset to pending for re-review."""
        self.write({"state": "pending", "date_approved": False})
