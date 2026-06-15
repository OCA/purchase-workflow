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

    def _prepare_purchase_order_line(
        self,
        name,
        product_qty=0.0,
        price_unit=0.0,
        taxes_ids=False,
    ):
        values = super()._prepare_purchase_order_line(
            name=name,
            product_qty=product_qty,
            price_unit=price_unit,
            taxes_ids=taxes_ids,
        )
        # tax computation
        # on purchase requisitions without a company_id
        company_id = self.env.context.get("order_company_id")
        partner_id = self.env.context.get("order_partner_id")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            partner = self.env["res.partner"].browse(partner_id)
            if not partner:
                partner = self.requisition_id.vendor_id
            fpos = (
                self.env["account.fiscal.position"]
                .with_company(company)
                ._get_fiscal_position(partner)
            )
            taxes = self.product_id.supplier_taxes_id.filtered(
                lambda tax: tax.company_id in company.parent_ids
            )
            values["taxes_id"] = [(6, 0, fpos.map_tax(taxes).ids)]
        return values
