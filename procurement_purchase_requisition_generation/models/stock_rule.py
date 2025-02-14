# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import SUPERUSER_ID, api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_purchase_requisition_domain(self, company_id, values):
        group = values.get("group_id")
        domain = (
            ("state", "=", "draft"),
            ("company_id", "=", company_id.id),
        )
        if group:
            domain += (("procurement_group_id", "=", group.id),)
        return domain

    def _prepare_purchase_requisition(self, company_id, origins, values):
        values = values[0]
        warehouse = values.get("warehouse_id")
        group = values.get("group_id")
        return {
            "origin": ", ".join(origins),
            "date_end": values["date_planned"],
            "user_id": False,
            "warehouse_id": warehouse.id if warehouse else False,
            "procurement_group_id": group.id if group else False,
            "company_id": company_id.id,
        }

    def _prepare_purchase_requisition_line(
        self, product_id, product_qty, product_uom, values
    ):
        return {
            "product_id": product_id.id,
            "product_uom_id": product_uom.id,
            "product_qty": product_qty,
            "move_dest_id": values.get("move_dest_ids")
            and values["move_dest_ids"][0].id
            or False,
        }

    @api.model
    def _run_buy(self, procurements):
        procurements_by_pr_domain = defaultdict(list)
        other_procurements = []
        requisition_model = self.env["purchase.requisition"].sudo()
        for procurement, rule in procurements:
            if procurement.product_id.purchase_requisition == "tenders":
                domain = rule._make_purchase_requisition_domain(
                    procurement.company_id, procurement.values
                )
                procurements_by_pr_domain[domain].append((procurement, rule))
            else:
                other_procurements.append((procurement, rule))
        for domain, procurements_rules in procurements_by_pr_domain.items():
            procurements, rules = zip(*procurements_rules, strict=True)
            origins = set([p.origin for p in procurements])
            requisition = requisition_model.search([dom for dom in domain], limit=1)
            company_id = procurements[0].company_id
            if not requisition:
                values = [p.values for p in procurements]
                vals = rules[0]._prepare_purchase_requisition(
                    company_id, origins, values
                )
                vals["picking_type_id"] = rule.picking_type_id.id
                requisition = (
                    requisition_model.with_company(company_id)
                    .with_user(SUPERUSER_ID)
                    .create(vals)
                )
            requistion_line_values = []
            for procurement in procurements:
                line_values = rules[0]._prepare_purchase_requisition_line(
                    procurement.product_id,
                    procurement.product_qty,
                    procurement.product_uom,
                    procurement.values,
                )
                requistion_line_values.append((0, 0, line_values))
            requisition.write({"line_ids": requistion_line_values})
        return super()._run_buy(other_procurements)
