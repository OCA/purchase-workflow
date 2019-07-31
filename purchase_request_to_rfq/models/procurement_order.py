# -*- coding: utf-8 -*-
# Copyright 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _check(self):
        po_line = self.purchase_line_id
        if po_line.purchase_request_lines:
            request_lines = po_line.purchase_request_lines.filtered(
                lambda x: x.procurement_id.id == self.id)
            if not self.move_ids:
                if request_lines.purchase_state in (
                    'purchase', 'done', 'cancel'
                ):
                    return True
                else:
                    return False

            move_all_done_or_cancel = all(
                move.state in ['done', 'cancel'] for move in self.move_ids)
            move_all_cancel = all(
                move.state == 'cancel' for move in self.move_ids)
            if not move_all_done_or_cancel:
                return False
            if move_all_cancel:
                # if a PO has been canceled after validation.
                # the procurement should be still running.
                # no need to be in exception here because
                # the purchase state is managed on the purchase request
                return False
            else:
                return True
        return super(ProcurementOrder, self)._check()
