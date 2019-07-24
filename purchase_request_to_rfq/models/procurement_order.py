# -*- coding: utf-8 -*-
# Copyright 2016-2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, fields, models, exceptions


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _check(self):
        if self.request_id:
            request_lines = self.request_id.line_ids.filtered(
                lambda x: x.procurement_id.id == self.id)
            if not self.move_ids:
                if request_lines.purchase_state not in ('purchase', 'done', 'cancel'):
                    return False
                else:
                    return True
            move_all_done_or_cancel = all(move.state in ['done', 'cancel'] for move in self.move_ids)
            move_all_cancel = all(move.state == 'cancel' for move in self.move_ids)
            if not move_all_done_or_cancel:
                return False
            elif move_all_done_or_cancel and not move_all_cancel:
                return True
            else:
                self.message_post(body=_('All stock moves have been cancelled for this procurement.'))
                self.write({'state': 'cancel'})
                return False
        return super(ProcurementOrder, self)._check()
