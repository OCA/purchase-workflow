# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade_merge_records

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MergePurchaseAutomatic(models.TransientModel):
    """
    The idea behind this wizard is to create a list of potential purchases
    to merge. We use two objects, the first one is the wizard for
    the end-user. And the second will contain the purchase list to merge.
    """

    _name = "purchase.merge.automatic.wizard"

    purchase_ids = fields.Many2many(
        comodel_name="purchase.order",
    )
    dst_purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Destination",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(MergePurchaseAutomatic, self).default_get(fields_list)
        active_ids = self.env.context.get("active_ids")
        purchase_orders = self.purchase_ids.browse(active_ids)
        self._check_all_values(purchase_orders)
        if (
            self.env.context.get("active_model") == "purchase.order"
            and len(active_ids) >= 1
        ):
            res["purchase_ids"] = [(6, 0, active_ids)]
            res["dst_purchase_id"] = self._get_ordered_purchase(active_ids)[-1].id
        return res

    # ----------------------------------------
    # Check method
    # ----------------------------------------

    def _check_all_values(self, purchase_orders):
        """Contain all check method"""
        self._check_state(purchase_orders)
        self._check_content(purchase_orders)

    def _check_state(self, purchase_orders):
        non_draft_po = purchase_orders.filtered(lambda p: p.state != "draft")
        if non_draft_po:
            po_names = non_draft_po.mapped("name")
            raise ValidationError(
                _(
                    "You can't merge purchase orders that aren't in draft state like: {}"
                ).format(po_names)
            )

    def _check_content(self, purchase_orders):
        error_messages = []

        currencies = purchase_orders.currency_id
        if len(currencies) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different currencies: %s",
                    ", ".join(currencies.mapped("name")),
                )
            )
        picking_types = purchase_orders.picking_type_id
        if len(picking_types) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different picking types: %s",
                    ", ".join(picking_types.mapped("name")),
                )
            )

        incoterms = purchase_orders.incoterm_id
        if len(incoterms) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different incoterms: %s",
                    ", ".join(incoterms.mapped("name")),
                )
            )

        payment_terms = purchase_orders.payment_term_id
        if len(payment_terms) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different payment terms: %s",
                    ", ".join(payment_terms.mapped("name")),
                )
            )

        fiscal_positions = purchase_orders.fiscal_position_id
        if len(fiscal_positions) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different fiscal positions: %s",
                    ", ".join(fiscal_positions.mapped("name")),
                )
            )

        suppliers = purchase_orders.partner_id
        if len(suppliers) > 1:
            error_messages.append(
                _(
                    "You can't merge purchase orders with different suppliers: %s",
                    ", ".join(suppliers.mapped("name")),
                )
            )

        if error_messages:
            raise ValidationError("\n".join(error_messages))

    # ----------------------------------------
    # Update method
    # ----------------------------------------

    @api.model
    def _update_values(self, src_purchase, dst_purchase):
        """Update values of dst_purchase with the ones from the src_purchase.
        :param src_purchase : recordset of source purchase.order
        :param dst_purchase : record of destination purchase.order
        """
        # merge all order lines + set origin and partner_ref
        dst_purchase.write(self._get_update_values(src_purchase, dst_purchase))
        for po in src_purchase:
            self._add_message("to", [dst_purchase.name], po)

        po_names = src_purchase.mapped("name")
        self._add_message("from", po_names, dst_purchase)

    @api.model
    def _get_update_values(self, src_purchase, dst_purchase):
        """Generate values of dst_purchase with the ones from the src_purchase.
        :param src_purchase : recordset of source purchase.order
        :param dst_purchase : record of destination purchase.order
        """
        # initialize destination origin and partner_ref
        origin = {dst_purchase.origin or ""}
        origin.update({x.origin for x in src_purchase if x.origin})

        partner_ref = {dst_purchase.partner_ref or ""}
        partner_ref.update({x.partner_ref for x in src_purchase if x.partner_ref})

        # Generate destination origin and partner_ref
        src_order_line = src_purchase.mapped("order_line")

        return {
            "order_line": [(4, line, 0) for line in src_order_line.ids],
            "origin": ", ".join(origin),
            "partner_ref": ", ".join(partner_ref),
        }

    def _add_message(self, way, po_name, po):
        """Send a message post with to advise the po about the merge.
        :param way : choice between 'from' or 'to'
        :param po_name : list of purchase order name to add in the body
        :param po_name : the po where the message will be posted
        """
        subject = "Merge purchase order"
        body = _(
            "This purchase order lines have been merged {way} : {po_names}",
            way=way,
            po_names=" ,".join(po_name),
        )

        po.message_post(body=body, subject=subject, content_subtype="plaintext")

    def _merge(self, purchases, dst_purchase=None):
        """private implementation of merge purchase
        :param purchases : ids of purchase to merge
        :param dst_purchase : record of destination purchase.order
        """
        if len(purchases) < 2:
            return
        record_ids = purchases - dst_purchase
        openupgrade_merge_records.merge_records(
            env=self.env,
            model_name=self._name,
            record_ids=record_ids.ids,
            target_record_id=dst_purchase.id,
        )
        self._check_all_values(purchases)

        # remove dst_purchase from purchases to merge
        if dst_purchase and dst_purchase in purchases:
            src_purchase = purchases - dst_purchase
        else:
            dst_purchase = self.purchase_ids[-1]
            src_purchase = self.purchase_ids[:-1]
        # call sub methods to do the merge
        self._update_values(src_purchase, dst_purchase)

        # cancel source purchase, since they are merged
        src_purchase.button_cancel()

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    @api.model
    def _get_ordered_purchase(self, purchase_ids):
        """Helper returns a `purchase.order` recordset ordered by create_date
        :param purchase_ids : list of purchase ids to sort
        """
        return (
            self.env["purchase.order"]
            .browse(purchase_ids)
            .sorted(
                key=lambda p: (p.create_date or ""),
                reverse=True,
            )
        )

    # ----------------------------------------
    # Actions
    # ----------------------------------------

    def action_merge(self):
        """Merge Quotation button. Merge the selected purchases."""
        if not self.purchase_ids:
            return False
        self._merge(self.purchase_ids, self.dst_purchase_id)
        return True
