from odoo import api, fields, models


class PurchaseInvoincingPickingFilter(models.TransientModel):
    _name = "purchase.invoicing.picking.filter"

    purchase_order_ids = fields.Many2many(
        "purchase.order", default=lambda self: self.env.context.get("active_ids")
    )
    stock_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Pickings",
        domain="""
            [
                ('purchase_id', 'in', purchase_order_ids),
                ('state', '=', 'done'),
                ('invoiced', '=', False),
            ]
        """,
    )
    inv_service_products = fields.Boolean(
        string="Invoice Service Products",
        compute="_compute_invoice_service_products",
        readonly=False,
        store=True,
        help="If selected and there is a service type " "product, it will be invoiced.",
    )
    there_are_service_product = fields.Boolean(
        string="There are a Service Product",
        compute="_compute_invoice_service_products",
        store=True,
    )
    count = fields.Integer(string="Order Count", compute="_compute_count")
    company_id = fields.Many2one(
        comodel_name="res.company", compute="_compute_company_id", store=True
    )

    @api.depends("purchase_order_ids")
    def _compute_count(self):
        for wizard in self:
            wizard.count = len(wizard.purchase_order_ids)

    @api.depends("purchase_order_ids")
    def _compute_company_id(self):
        self.company_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.company_id = wizard.purchase_order_ids.company_id

    @api.depends("stock_picking_ids")
    def _compute_invoice_service_products(self):
        for sel in self:
            res = False
            service_lines = (
                sel.stock_picking_ids.mapped("purchase_id")
                .mapped("order_line")
                .filtered(
                    lambda x: x.invoice_status == "to invoice"
                    and x.product_id.type == "service"
                )
            )
            if service_lines:
                res = True
            sel.inv_service_products = res
            sel.there_are_service_product = res

    def create_invoices(self):
        self._create_invoices(self.purchase_order_ids)

        if self.env.context.get("open_invoices"):
            return self.purchase_order_ids.action_view_invoice()

        return {"type": "ir.actions.act_window_close"}

    def _create_invoices(self, purchase_orders):
        self.ensure_one()
        self = self.with_company(self.company_id)
        order = self.purchase_order_ids

        if self.stock_picking_ids:
            invoice = purchase_orders.with_context(
                invoice_service_products=self.inv_service_products
            )._create_invoices_from_pickings(self.stock_picking_ids)
        else:
            return purchase_orders.action_create_invoice()

        invoice.message_post_with_view(
            "mail.message_origin_link",
            values={"self": invoice, "origin": order},
            subtype_id=self.env.ref("mail.mt_note").id,
        )

        return invoice
