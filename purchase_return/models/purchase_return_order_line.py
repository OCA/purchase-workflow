from odoo import api, fields, models


class PurchaseReturnOrderLine(models.Model):
    _name = "purchase.return.order.line"
    _inherit = "purchase.order.line"
    _description = "Purchase Return Order Line"
    _order = "order_id, sequence, id"

    date_planned = fields.Datetime(
        string="Delivery Date",
        help="Delivery date expected from vendor. "
        "This date respectively defaults to vendor pricelist "
        "lead time then today's date.",
    )
    order_id = fields.Many2one(
        "purchase.return.order",
        string="Order Reference",
        index=True,
        required=True,
        ondelete="cascade",
    )
    invoice_lines = fields.One2many(
        "account.move.line",
        "purchase_return_line_id",
        string="Bill Lines",
        readonly=True,
        copy=False,
    )
    # Replace by invoiced Qty
    qty_invoiced = fields.Float(
        compute="_compute_qty_invoiced",
        string="Refunded Qty",
        digits="Product Unit of Measure",
        store=True,
    )
    refund_only = fields.Boolean(string="Refund only")

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "refund_only",
        "product_uom_qty",
        "order_id.state",
    )
    def _compute_qty_invoiced(self):
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ["cancel"]:
                    if inv_line.move_id.move_type == "in_invoice":
                        qty -= inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.product_uom
                        )
                    elif inv_line.move_id.move_type == "in_refund":
                        qty += inv_line.product_uom_id._compute_quantity(
                            inv_line.quantity, line.product_uom
                        )
            line.qty_invoiced = qty

            # compute qty_to_invoice
            if line.order_id.state in ["purchase", "done"]:
                line.qty_to_invoice = line.product_qty - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.model
    def _prepare_purchase_return_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        partner = supplier.name
        uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_po_id)
        # _select_seller is used if the supplier have different price depending
        # the quantities ordered.
        seller = product_id.with_company(company_id)._select_seller(
            partner_id=partner,
            quantity=uom_po_qty,
            date=po.date_order and po.date_order.date(),
            uom_id=product_id.uom_po_id,
        )

        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes, product_id, seller.name)
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == company_id.id)

        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.price, product_id.supplier_taxes_id, taxes_id, company_id
            )
            if seller
            else 0.0
        )
        if (
            price_unit
            and seller
            and po.currency_id
            and seller.currency_id != po.currency_id
        ):
            price_unit = seller.currency_id._convert(
                price_unit,
                po.currency_id,
                po.company_id,
                po.date_order or fields.Date.today(),
            )

        product_lang = product_id.with_prefetch().with_context(
            lang=partner.lang,
            partner_id=partner.id,
        )
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += "\n" + product_lang.description_purchase

        date_planned = self.order_id.date_planned or self._get_date_planned(
            seller, po=po
        )

        return {
            "name": name,
            "product_qty": uom_po_qty,
            "product_id": product_id.id,
            "product_uom": product_id.uom_po_id.id,
            "price_unit": price_unit,
            "date_planned": date_planned,
            "taxes_id": [(6, 0, taxes_id.ids)],
            "order_id": po.id,
        }

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = {
            "display_type": self.display_type,
            "sequence": self.sequence,
            "name": "%s: %s" % (self.order_id.name, self.name),
            "product_id": self.product_id.id,
            "product_uom_id": self.product_uom.id,
            "quantity": self.qty_to_invoice,
            "price_unit": self.price_unit,
            "tax_ids": [(6, 0, self.taxes_id.ids)],
            "analytic_account_id": self.account_analytic_id.id,
            "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
            "purchase_return_line_id": self.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update(
            {
                "move_id": move.id,
                "currency_id": currency and currency.id or False,
                "date_maturity": move.invoice_date_due,
                "partner_id": move.partner_id.id,
            }
        )
        return res
