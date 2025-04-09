from odoo import api, fields, models


class PurchaseContainer(models.Model):
    _name = "purchase.container"
    _description = "Purchase order related container"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True, readonly=True, index=True)
    code = fields.Char(
        string="Container Reference",
        compute="_compute_code",
        inverse="_inverse_code",
        store=True,
        required=True,
        copy=False,
    )
    bill_of_lading_ref = fields.Char("Bill Of Lading No.", copy=False)
    shipping_agent_id = fields.Many2one(
        comodel_name="res.partner", string="Shipping Agent"
    )
    type_id = fields.Many2one(comodel_name="container.type")
    package_qty = fields.Integer(copy=False)
    cost = fields.Float(digits="Product Price", copy=False)
    cost_currency_id = fields.Many2one("res.currency", "Cost Currency", copy=False)
    volume = fields.Float(digits="Volume", copy=False)
    volume_uom_id = fields.Many2one(
        "uom.uom",
        string="Volume Units of Measure",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id)
        ],
        default=lambda self: self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter(),
    )
    weight = fields.Float(string="Bruto Weight", digits="Stock Weight", copy=False)
    weight_uom_id = fields.Many2one(
        "uom.uom",
        string="Weight Units of Measure",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id)
        ],
        help="Weight Unit of Measure",
        default=lambda self: self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter(),
    )
    purchase_order_ids = fields.Many2many(
        "purchase.order", string="Related Purchases", copy=False
    )
    purchase_order_count = fields.Integer(
        string="Purchases", compute="_compute_purchase_order_count"
    )
    purchase_order_rfq_count = fields.Integer(
        string="RFQ", compute="_compute_purchase_order_rfq_count"
    )
    picking_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="container_id",
        string="Related Pickings",
    )
    picking_count = fields.Integer(string="Receipts", compute="_compute_picking_count")

    @api.depends("code", "purchase_order_ids")
    def _compute_name(self):
        for record in self:
            record.name = record.code
            po = record.purchase_order_ids
            if po:
                record.name += " ({})".format(",".join(po.mapped("name")))

    @api.model
    def _code_transform(self, code):
        return code.upper() if code else code

    @api.model
    def _code_from_name(self, name):
        words = name.split() if name else None
        code = words[0] if words else False
        return self._code_transform(code)

    @api.depends("name")
    def _compute_code(self):
        for record in self:
            if not record.code:
                record.code = record._code_from_name(record.name)

    def _inverse_code(self):
        for record in self:
            code = self._code_transform(record.code)
            if record.code != code:
                record.code = code

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("code", self._code_from_name(vals.get("name")))
        return super().create(vals_list=vals_list)

    def _compute_purchase_order_count(self):
        for record in self:
            record.purchase_order_count = self.env["purchase.order"].search_count(
                [
                    ("state", "in", ("purchase", "done")),
                    ("container_ids", "=", self.id),
                ],
            )

    def _compute_purchase_order_rfq_count(self):
        for record in self:
            record.purchase_order_rfq_count = self.env["purchase.order"].search_count(
                [
                    ("state", "in", ("draft", "sent", "to approve")),
                    ("container_ids", "=", self.id),
                ],
            )

    def _compute_picking_count(self):
        for record in self:
            record.picking_count = len(record.picking_ids)

    def action_view_rfq(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        action["domain"] = [
            (
                "id",
                "in",
                [
                    po.id
                    for po in self.purchase_order_ids
                    if po.state in ("draft", "sent", "to approve")
                ],
            )
        ]
        action["context"] = {"create": False}
        return action

    def action_view_order(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase.purchase_form_action"
        )
        action["domain"] = [
            (
                "id",
                "in",
                [
                    po.id
                    for po in self.purchase_order_ids
                    if po.state in ("purchase", "done")
                ],
            )
        ]
        action["context"] = {"create": False}
        return action

    def action_view_picking(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        action["domain"] = [("id", "in", self.picking_ids.ids)]
        action["context"] = {"create": False}
        return action
