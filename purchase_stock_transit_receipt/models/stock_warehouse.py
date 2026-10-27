# Copyright 2026 Akretion
# @author Guillaume MASSON <guillaume.masson@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    incoming_transit_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Incoming Transit Location",
        check_company=True,
        copy=False,
    )
    transit_in_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Transit Receipt Type",
        check_company=True,
        copy=False,
    )

    def _get_incoming_transit_location_name(self, code=False):
        return _("%(code)s: Incoming transit", code=code or self.code)

    def _get_incoming_transit_location_values(self):
        return {
            "name": self._get_incoming_transit_location_name(),
            "usage": "transit",
            "location_id": self.env.ref("stock.stock_location_locations").id,
            "company_id": self.company_id.id,
        }

    def _create_or_update_sequences_and_picking_types(self):
        if not self.incoming_transit_location_id:
            self.incoming_transit_location_id = self.env["stock.location"].create(
                self._get_incoming_transit_location_values()
            )
        warehouse_data = super()._create_or_update_sequences_and_picking_types()
        if "transit_in_type_id" in warehouse_data:
            self.env["stock.picking.type"].browse(
                warehouse_data["transit_in_type_id"]
            ).return_picking_type_id = warehouse_data.get(
                "out_type_id", self.out_type_id.id
            )
        return warehouse_data

    def _get_picking_type_create_values(self, max_sequence):
        values, max_sequence = super()._get_picking_type_create_values(max_sequence)
        values["transit_in_type_id"] = {
            "name": _("Transit Receipts"),
            "code": "incoming",
            "use_existing_lots": False,
            "sequence": max_sequence + 1,
            "sequence_code": "TR",
            "company_id": self.company_id.id,
        }
        return values, max_sequence + 2

    def _get_picking_type_update_values(self):
        values = super()._get_picking_type_update_values()
        values["transit_in_type_id"] = {
            "default_location_dest_id": self.incoming_transit_location_id.id,
            "barcode": self.code.replace(" ", "").upper() + "TR",
        }
        return values

    def _get_sequence_values(self, name=False, code=False):
        values = super()._get_sequence_values(name=name, code=code)
        name = name or self.name
        code = code or self.code
        values["transit_in_type_id"] = {
            "name": _("%(name)s Sequence transit receipt", name=name),
            "prefix": code
            + "/"
            + (self.transit_in_type_id.sequence_code or "TR")
            + "/",
            "padding": 5,
            "company_id": self.company_id.id,
        }
        return values

    def _update_name_and_code(self, name=False, code=False):
        res = super()._update_name_and_code(name, code)
        for warehouse in self:
            if code:
                warehouse.incoming_transit_location_id.name = (
                    warehouse._get_incoming_transit_location_name(code)
                )
            sequence_data = warehouse._get_sequence_values(name=name, code=code)
            if self.env.user.has_group("stock.group_stock_manager"):
                warehouse = warehouse.sudo()
            warehouse.transit_in_type_id.sequence_id.write(
                sequence_data["transit_in_type_id"]
            )
        return res

    def _get_transit_receipt_routing(self):
        input_location, __ = self._get_input_output_locations(
            self.reception_steps, self.delivery_steps
        )
        return self.Routing(
            self.incoming_transit_location_id,
            input_location,
            self.in_type_id,
            "push",
        )

    def _create_or_update_transit_receipt_rule(self):
        self.reception_route_id.rule_ids.filtered(
            lambda rule: rule.location_src_id == self.incoming_transit_location_id
        ).active = False
        self._find_existing_rule_or_create(
            self._get_rule_values(
                [self._get_transit_receipt_routing()],
                values={"route_id": self.reception_route_id.id, "active": True},
            )
        )

    def _create_or_update_route(self):
        res = super()._create_or_update_route()
        self._create_or_update_transit_receipt_rule()
        return res

    def _setup_transit_receipt(self):
        for warehouse in self:
            warehouse.write(warehouse._create_or_update_sequences_and_picking_types())
            warehouse._create_or_update_transit_receipt_rule()
