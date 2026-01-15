from odoo import api, fields, models


class ContainerCostLine(models.Model):
    """Track individual cost components for a container.

    Allows detailed breakdown of all costs associated with importing a container:
    - Ocean freight (from freight forwarder like RL Swearer)
    - Drayage/local trucking
    - Customs holds and fees
    - Tariffs and duties
    - Per diem charges
    - Other miscellaneous fees
    """

    _name = "container.cost.line"
    _description = "Container Cost Line"
    _order = "container_id, sequence, id"

    container_id = fields.Many2one(
        "purchase.container",
        string="Container",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)

    cost_type = fields.Selection(
        [
            ("ocean_freight", "Ocean Freight"),
            ("drayage", "Drayage / Local Freight"),
            ("customs_hold", "Customs Hold"),
            ("tariff", "Tariffs / Duties"),
            ("per_diem", "Per Diem"),
            ("storage", "Storage Fees"),
            ("documentation", "Documentation Fees"),
            ("inspection", "Inspection Fees"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    name = fields.Char(
        string="Description",
        required=True,
        help="Description of the cost",
    )
    amount = fields.Monetary(
        currency_field="currency_id",
        required=True,
        help="Cost amount",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # Link to vendor/invoice
    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        help="Vendor who charged this cost",
    )
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        domain=[("move_type", "=", "in_invoice")],
        help="Related vendor bill",
    )
    invoice_line_id = fields.Many2one(
        "account.move.line",
        string="Invoice Line",
        domain="[('move_id', '=', invoice_id)]",
        help="Specific invoice line for this cost",
    )

    # Additional info
    date = fields.Date(
        default=fields.Date.context_today,
        help="Date of the cost/charge",
    )
    notes = fields.Text(help="Additional notes about this cost")

    @api.onchange("cost_type")
    def _onchange_cost_type(self):
        """Set default name based on cost type."""
        if self.cost_type and not self.name:
            type_labels = dict(self._fields["cost_type"].selection)
            self.name = type_labels.get(self.cost_type, "")

    @api.onchange("invoice_line_id")
    def _onchange_invoice_line_id(self):
        """Auto-fill from invoice line."""
        if self.invoice_line_id:
            self.amount = self.invoice_line_id.price_subtotal
            self.partner_id = self.invoice_line_id.partner_id
            if not self.name:
                self.name = self.invoice_line_id.name

    def name_get(self):
        result = []
        for line in self:
            name = f"{line.container_id.code}: {line.name}"
            if line.amount:
                symbol = line.currency_id.symbol or ""
                name += f" ({symbol}{line.amount:,.2f})"  # noqa: E231
            result.append((line.id, name))
        return result
