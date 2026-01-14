from datetime import date

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
    seal_number = fields.Char("Seal #", copy=False, help="Container seal number")
    shipping_agent_id = fields.Many2one(
        comodel_name="res.partner",
        string="Freight Forwarder",
        help="Freight forwarding company (e.g., RL Swearer)",
    )
    freight_forwarder_ref = fields.Char(
        help="Freight forwarder booking/reference number (e.g., RL Swearer ID: B00064516)",
        tracking=True,
    )
    drayage_company_id = fields.Many2one(
        comodel_name="res.partner",
        string="Drayage Company",
        help="Local drayage/trucking company for final delivery",
    )
    type_id = fields.Many2one(comodel_name="container.type")
    package_qty = fields.Integer(copy=False)
    cost = fields.Float(digits="Product Price", copy=False, string="Ocean Freight Cost")
    cost_currency_id = fields.Many2one("res.currency", "Cost Currency", copy=False)
    has_additional_fees = fields.Boolean(
        string="Has Add'l Fees",
        help="Check if there are per diem or additional fees to note",
    )
    per_diem_fees = fields.Float(
        digits="Product Price",
        copy=False,
        string="Per Diem / Add'l Fees",
        help="Per diem and additional fees amount",
    )
    per_diem_reason = fields.Text(
        "Fee Reason", help="Reason for per diem or additional fees"
    )
    notes = fields.Text(help="Internal notes about this container")
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

    incoterm_id = fields.Many2one(
        "account.incoterms", compute="_compute_incoterm_id", store=False, readonly=True
    )
    manual_incoterm_id = fields.Many2one("account.incoterms")
    displayed_incoterm_id = fields.Many2one(
        "account.incoterms",
        compute="_compute_displayed_incoterm_id",
        inverse="_inverse_displayed_incoterm_id",
        store=True,
        tracking=True,
    )

    departure_location_id = fields.Many2one(
        "res.partner", string="Port of Lading", help="Origin port"
    )
    arrival_location_id = fields.Many2one(
        "res.partner", string="Port of Discharge", help="Destination port"
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Destination Warehouse",
        help="Final destination warehouse (PA, ID, GA)",
    )
    date_eta = fields.Date(
        string="Port ETA", help="Estimated Time Of Arrival at Port", tracking=True
    )
    date_etd = fields.Date(
        string="ETD Date", help="Estimated Time Of Departure", tracking=True
    )
    date_warehouse_eta = fields.Date(
        string="Warehouse ETA",
        help="Estimated Time Of Arrival at final warehouse",
        tracking=True,
    )
    date_ata = fields.Date(
        string="ATA Date", help="Actual Time Of Arrival at Port", tracking=True
    )
    date_atd = fields.Date(
        string="ATD Date", help="Actual Time Of Departure", tracking=True
    )
    date_delivered = fields.Date(
        string="Delivered Date",
        help="Date container was delivered to warehouse",
        tracking=True,
    )
    date_received = fields.Date(
        string="Received Date",
        help="Date inventory was received into system",
        tracking=True,
    )
    date_ett = fields.Char(
        string="ETT Date",
        help="Estimated Time Of Travel",
        compute="_compute_date_ett",
        store=False,
        tracking=True,
    )

    state = fields.Selection(
        [
            ("in_progress", "In Progress"),
            ("pos_confirmed", "POs Confirmed"),
            ("freight_notified", "Freight Forwarder Notified"),
            ("on_water", "On the Water"),
            ("arrival_notice", "Arrival Notice"),
            ("drayage_confirmed", "Drayage Confirmed"),
            ("awaiting_gate_out", "Awaiting Gate Out"),
            ("customs_hold", "Customs Hold"),
            ("released", "Released for Delivery"),
            ("delivered", "Delivered"),
            ("received", "Received"),
            ("on_hold", "On Hold"),
            ("ready_to_process", "Ready to Process"),
            ("processed", "Processed"),
        ],
        default="in_progress",
        tracking=True,
        copy=False,
    )
    is_locked = fields.Boolean()

    # Document tracking
    document_ids = fields.One2many(
        "container.document",
        "container_id",
        string="Documents",
    )
    document_count = fields.Integer(compute="_compute_document_count")
    documents_complete = fields.Boolean(
        string="Docs Complete",
        compute="_compute_documents_complete",
        store=True,
        help="All required documents have been approved",
    )

    # Container line items
    line_ids = fields.One2many(
        "container.line",
        "container_id",
        string="Container Lines",
    )
    line_count = fields.Integer(string="Lines", compute="_compute_line_count")

    # Shipment tracking
    carrier_id = fields.Many2one(
        "res.partner",
        string="Shipping Carrier",
        help="Ocean carrier / shipping line (e.g., Maersk, MSC, COSCO)",
    )
    vessel_name = fields.Char(help="Name of the vessel/ship")
    voyage_number = fields.Char(help="Voyage or trip number")
    tracking_number = fields.Char(
        help="Carrier tracking number or booking reference",
        tracking=True,
    )
    tracking_url = fields.Char(
        compute="_compute_tracking_url",
        help="URL to track shipment on carrier website",
    )
    last_tracking_update = fields.Datetime(
        help="When tracking information was last updated",
    )
    tracking_status = fields.Char(help="Latest status from carrier tracking")

    # Landed cost integration
    landed_cost_ids = fields.Many2many(
        "stock.landed.cost",
        string="Landed Costs",
        help="Landed cost records associated with this container",
    )
    landed_cost_count = fields.Integer(compute="_compute_landed_cost_count")
    total_landed_cost = fields.Monetary(
        compute="_compute_total_landed_cost",
        currency_field="cost_currency_id",
        help="Total landed costs applied to this container",
    )

    def _compute_incoterm_id(self):
        for record in self:
            record.incoterm_id = record.purchase_order_ids.filtered(
                lambda po: po.incoterm_id
            )[:1].incoterm_id

    @api.depends(
        "manual_incoterm_id", "purchase_order_ids", "purchase_order_ids.incoterm_id"
    )
    def _compute_displayed_incoterm_id(self):
        for record in self:
            record.displayed_incoterm_id = (
                record.manual_incoterm_id
                if record.manual_incoterm_id
                else record.incoterm_id
            )

    def _inverse_displayed_incoterm_id(self):
        for record in self:
            record.manual_incoterm_id = record.displayed_incoterm_id

    @api.depends("date_eta", "date_etd")
    def _compute_date_ett(self):
        for record in self:
            record.date_ett = 0
            if record.date_eta and record.date_etd:
                record.date_ett = record.date_eta - record.date_etd

    def button_lock(self):
        """Lock the container to prevent further changes."""
        self.is_locked = True

    def button_unlock(self):
        """Unlock the container to allow changes."""
        self.is_locked = False

    def action_set_on_water(self):
        """Mark container as on the water (departed)."""
        self.write({"state": "on_water", "date_atd": date.today()})

    def action_set_arrival_notice(self):
        """Mark container as having arrival notice."""
        self.write({"state": "arrival_notice"})

    def action_set_delivered(self):
        """Mark container as delivered to warehouse."""
        self.write({"state": "delivered", "date_delivered": date.today()})

    def action_set_received(self):
        """Mark container as received into inventory."""
        self.write({"state": "received", "date_received": date.today()})

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

    # Document tracking methods
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)

    @api.depends("document_ids.state", "document_ids.required")
    def _compute_documents_complete(self):
        for record in self:
            required_docs = record.document_ids.filtered(lambda d: d.required)
            record.documents_complete = (
                all(doc.state == "approved" for doc in required_docs)
                if required_docs
                else True
            )

    def action_view_documents(self):
        self.ensure_one()
        return {
            "name": "Container Documents",
            "type": "ir.actions.act_window",
            "res_model": "container.document",
            "view_mode": "list,form",
            "domain": [("container_id", "=", self.id)],
            "context": {"default_container_id": self.id},
        }

    def action_create_required_documents(self):
        """Create document records for all required document types."""
        self.ensure_one()
        required_types = self.env["container.document.type"].search(
            [("required", "=", True)]
        )
        existing_types = self.document_ids.mapped("document_type_id")
        for doc_type in required_types - existing_types:
            self.env["container.document"].create(
                {
                    "container_id": self.id,
                    "document_type_id": doc_type.id,
                }
            )
        return True

    # Container line methods
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    def action_view_lines(self):
        self.ensure_one()
        return {
            "name": "Container Lines",
            "type": "ir.actions.act_window",
            "res_model": "container.line",
            "view_mode": "list,form",
            "domain": [("container_id", "=", self.id)],
            "context": {"default_container_id": self.id},
        }

    # Shipment tracking methods
    def _compute_tracking_url(self):
        """Generate tracking URL based on carrier.

        This can be extended to support different carrier tracking portals.
        """
        for record in self:
            url = False
            if record.tracking_number and record.carrier_id:
                carrier_name = (record.carrier_id.name or "").lower()
                tracking = record.tracking_number
                url = record._get_tracking_url_for_carrier(carrier_name, tracking)
            record.tracking_url = url

    def _get_tracking_url_for_carrier(self, carrier_name, tracking):
        """Get tracking URL for a specific carrier.

        Can be extended to add more carriers.
        """
        base_urls = {
            "maersk": "https://www.maersk.com/tracking/",
            "msc": "https://www.msc.com/track-a-shipment?agencyPath=msc&trackingNumber=",
            "cosco": "https://elines.coscoshipping.com/ebusiness/cargoTracking?trackNo=",
            "hapag": (
                "https://www.hapag-lloyd.com/en/online-business/track/"
                "track-by-container-solution.html?container="
            ),
            "one": (
                "https://ecomm.one-line.com/one-ecom/manage-shipment/"
                "cargo-tracking?trakNoParam="
            ),
            "evergreen": (
                "https://www.shipmentlink.com/tvs2/jsp/"
                "TVS2_ContainerTracking.jsp?cntr="
            ),
        }
        for key, url in base_urls.items():
            if key in carrier_name:
                return url + tracking
        # Generic tracking via searates
        return "https://www.searates.com/container/tracking/?number=" + tracking

    def action_open_tracking(self):
        """Open tracking URL in browser."""
        self.ensure_one()
        if self.tracking_url:
            return {
                "type": "ir.actions.act_url",
                "url": self.tracking_url,
                "target": "new",
            }
        return False

    # Landed cost methods
    def _compute_landed_cost_count(self):
        for record in self:
            record.landed_cost_count = len(record.landed_cost_ids)

    def _compute_total_landed_cost(self):
        for record in self:
            record.total_landed_cost = sum(
                lc.amount_total
                for lc in record.landed_cost_ids.filtered(lambda l: l.state == "done")
            )

    def action_view_landed_costs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock_landed_costs.action_stock_landed_cost"
        )
        action["domain"] = [("id", "in", self.landed_cost_ids.ids)]
        action["context"] = {"default_container_id": self.id}
        return action

    def action_create_landed_cost(self):
        """Create a new landed cost record for this container."""
        self.ensure_one()
        if not self.picking_ids:
            return False
        # Get done pickings for landed cost
        done_pickings = self.picking_ids.filtered(lambda p: p.state == "done")
        if not done_pickings:
            return False
        landed_cost = self.env["stock.landed.cost"].create(
            {
                "picking_ids": [(6, 0, done_pickings.ids)],
            }
        )
        self.landed_cost_ids = [(4, landed_cost.id)]
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.landed.cost",
            "view_mode": "form",
            "res_id": landed_cost.id,
        }
