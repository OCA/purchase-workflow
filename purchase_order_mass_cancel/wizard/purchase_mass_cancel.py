# -*- coding: utf-8 -*-
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError


class PurchaseMassCancelWizard(models.TransientModel):
    _name = "purchase.mass.cancel.wizard"
    _description = "Purchase Mass Cancel Wizard"

    @api.multi
    def purchase_mass_cancel(self):
        purchase_obj = self.env['purchase.order']

        active_ids = self._context.get('active_ids')
        purchases = purchase_obj.browse(active_ids)
        for purchase in purchases:
            if purchase.state != 'draft':
                raise UserError(
                    _("All purchases must be in 'draft' state to cancel."))
        purchases.button_cancel()
        return True
