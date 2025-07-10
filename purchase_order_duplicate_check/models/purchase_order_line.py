from odoo import _, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pending_order_ids = fields.Many2many(
        "purchase.order",
        string="Pending Orders",
        compute="_compute_pending_order_ids",
    )

    def _compute_pending_order_ids(self):
        product_lines = self.filtered(lambda rec: rec.product_type == "product")
        other_lines = self - product_lines

        if other_lines:
            other_lines.pending_order_ids = False

        if not product_lines:
            return

        product_ids = tuple(product_lines.mapped("product_id")._origin.ids)
        order_ids = tuple(product_lines.mapped("order_id")._origin.ids)
        if not product_ids or not order_ids:
            product_lines.pending_order_ids = False
            return
        query = """
                SELECT po.id, pol.product_id
                FROM purchase_order po
                JOIN purchase_order_line pol ON pol.order_id = po.id
                LEFT JOIN stock_move sm ON sm.purchase_line_id = pol.id
                LEFT JOIN stock_picking sp ON sp.id = sm.picking_id

                WHERE pol.product_id IN %s
                    AND po.id NOT IN %s
                    AND (
                      po.state IN ('draft', 'sent')
                      OR (
                          po.state NOT IN ('draft', 'sent')
                          AND sp.picking_type_id IN (
                              SELECT id FROM stock_picking_type WHERE code = 'incoming'
                          )
                          AND sp.state NOT IN ('done', 'cancel')
                      )
                  )
            """
        self.env.cr.execute(query, (product_ids, order_ids))
        result = self.env.cr.fetchall()
        product_orders_map = {}
        for order_id, product_id in result:
            if product_id not in product_orders_map:
                product_orders_map[product_id] = []
            product_orders_map[product_id].append(order_id)

        for rec in product_lines:
            rec.pending_order_ids = [
                (6, 0, product_orders_map.get(rec.product_id.id, []))
            ]

    def _get_order_confirm_message(self):
        """Get order confirmation message for pending orders"""
        message = ""
        for line in self:
            pending_orders = line.pending_order_ids
            if not pending_orders:
                continue
            product_line_msg = pending_orders._prepare_pending_orders_message(
                line.product_id.id
            )
            message += f"""
            Product <b>{line.product_id.name}</b><br/>
            {product_line_msg}<br/>
            """
        return message

    def action_open_pending_orders(self):
        """Action open pending purchase orders"""
        self.ensure_one()
        return {
            "name": _("Pending Orders"),
            "views": [[False, "tree"], [False, "form"]],
            "res_model": "purchase.order",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", self.pending_order_ids.ids)],
            "context": {"create": False},
        }
