# Copyright 2019 RGB Consulting - Domantas Sidorenkovas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        if any(rec.partner_id.supplier_approve_status != 'approved' for rec in
               self):
            raise ValidationError(_('You cannot confirm a purchase order if'
                                    ' the supplier is not approved.'))
        return super(PurchaseOrder, self).button_confirm()
