from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _run_buy(self, procurements):
        rule_model = self.env["purchase.auto.validation"].sudo()
        for procurement, rule in procurements:
            domain = [
                "|",
                ("product_ids", "in", [procurement.product_id.id]),
                ("product_tmpl_ids", "in", [procurement.product_id.product_tmpl_id.id]),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", procurement.company_id.id),
            ]
            rule = rule_model.search(domain, limit=1)
            if rule:
                procurement.values["purchase_auto_validation_id"] = rule.id
        return super()._run_buy(procurements)

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        rule_id = values.get("purchase_auto_validation_id")
        if rule_id:
            rule = self.env["purchase.auto.validation"].sudo().browse(rule_id).exists()
            supplier = values.get("supplier")
            if supplier and supplier.name == rule.partner_id:
                domain = tuple(
                    leaf
                    for leaf in domain
                    if not (isinstance(leaf, tuple) and leaf[0] == "group_id")
                )
                return domain + (("purchase_auto_validation_id", "=", rule_id),)
        return domain + (("purchase_auto_validation_id", "=", False),)

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super()._prepare_purchase_order(company_id, origins, values)
        rule_id = values[0].get("purchase_auto_validation_id") if values else None
        if rule_id:
            vals["purchase_auto_validation_id"] = rule_id
        return vals
