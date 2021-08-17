# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, SUPERUSER_ID


def date(picking, datetime):
    # TODO: extract the tz field on the warehouse from the module
    # sale_cutoff_time_delivery in OCA/sale-workflow to make a generic module
    # on which this module can depend on. At the moment, we take the tz of the
    # SUPERUSER. This is safer than the tz of the user (purchaser)
    tz = picking.env['res.users'].sudo().browse(SUPERUSER_ID).tz
    picking = picking.with_context(tz=tz)
    return fields.Date.context_today(picking, datetime)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _is_valid_picking(self, picking):
        date_planned = date(picking, self.date_planned)
        return (
            picking.state not in ('done', 'cancel')
            and date(picking, picking.scheduled_date) == date_planned
            and picking.location_dest_id.usage in ('internal', 'transit', 'customer')
        )

    def _get_sorted_keys(self, line):
        """Return a tuple of keys to use in order to sort the order lines.
        This method is designed for extensibility, so that other modules can
        add additional keys or replace them by others."""
        return (line.date_planned,)

    def _create_stock_moves(self, picking):
        # _prepare_stock_moves needs previous move to be created to ensure the
        # new move is inserted in the right picking. So create move one by one.
        moves = self.env['stock.move']
        for line in self:
            moves |= super(PurchaseOrderLine, line)._create_stock_moves(picking)
        return moves

    def _prepare_stock_moves(self, picking):
        # When a quantity is increased on a confirmed PO line,
        # _create_or_update_picking is called to create a new move. That move
        # will always be inserted in the first picking linked to the PO. So, if the
        # planned date does not match, we need to provide another picking.
        # Afterwards, the move is created and then confirmed. This could cause
        # the move to be merged with another one. To allow this, the move must
        # be inserted in the right picking.
        if picking.move_lines and not self._is_valid_picking(picking):
            pickings = self.order_id.order_line.move_ids.picking_id
            picking = fields.first(pickings.filtered(
                lambda p: self._is_valid_picking(p)))
            if not picking:
                res = self.order_id._prepare_picking()
                picking = self.env['stock.picking'].create(res)
        return super()._prepare_stock_moves(picking)

    @api.model
    def _prepare_picking_copy_vals(self):
        """The data to be copied to new pickings. This method is designed for
        extensibility."""
        return {"move_lines": []}

    def _check_still_valid_picking(self):
        moves = self.move_ids.filtered(lambda m: m.state not in ('draft', 'done', 'cancel'))
        pickings = self.order_id.order_line.move_ids.filtered(
            lambda m: m.state not in ('draft', 'done', 'cancel')).picking_id
        picking_to_cancel = self.env['stock.picking']
        for move in moves:
            if self._is_valid_picking(move.picking_id):
                # If the move is the only move of the picking, the picking will
                # be valid (as the date will be computed as the move date) but
                # the move could possibly have been merged in another existing
                # picking
                if move != move.picking_id.move_lines:
                    continue
                picking = fields.first(pickings.filtered(
                    lambda p: p != move.picking_id and self._is_valid_picking(p)))
                if not picking:
                    # No other valid picking
                    continue
                picking_to_cancel |= move.picking_id
            else:
                # Find an other valid picking
                picking = fields.first(pickings.filtered(
                    lambda p: self._is_valid_picking(p)))
                if not picking:
                    copy_vals = self._prepare_picking_copy_vals()
                    picking = move.picking_id.copy(copy_vals)
                    pickings |= picking
            move._do_unreserve()
            move.picking_id = picking
            move._merge_moves()
            move._action_assign()
        picking_to_cancel.filtered(lambda p: not p.move_lines).write({"state": "cancel"})

    def write(self, values):
        res = super().write(values)
        if "date_planned" in values:
            for line in self.filtered(lambda l: not l.display_type):
                # The move date_expected could have changed
                line._check_still_valid_picking()
        return res
