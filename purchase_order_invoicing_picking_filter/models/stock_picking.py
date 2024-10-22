from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def name_get(self):
        res = []
        if not self.env.context.get("carrier_tracking_name", False):
            return super().name_get()
        for record in self:
            if record.carrier_tracking_ref:
                res.append(tuple([record.id, record.carrier_tracking_ref]))
            else:
                res.append(tuple([record.id, record.name]))
        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if self.env.context.get("carrier_tracking_name", False):
            recs = self.search(
                [('carrier_tracking_ref', operator, name)] + args, limit=limit
            )
            if not recs.ids:
                recs = self.search([("name", operator, name)] + args, limit=limit)
        else:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.depends("invoice_ids", "invoice_ids.state")
    def _compute_invoiced(self):
        invoiced_pickings = self._get_invoiced_pickings(
            "sale_id"
        ) | self._get_invoiced_pickings("purchase_id")
        invoiced_pickings.write({"invoiced": True})
        (self - invoiced_pickings).write({"invoiced": False})

    def _get_invoiced_pickings(self, id_field):
        return self.filtered(
            lambda a: getattr(a, id_field)
            and a.invoice_ids
            and any(invoice.state != "cancel" for invoice in a.invoice_ids)
            and a.picking_type_code in ["incoming", "outgoing"]
        )
