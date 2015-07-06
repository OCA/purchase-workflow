# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.multi
    def do_detailed_transfer_and_generate(self):
        """
        Do detailed transfer and once it's done, trigger the purchase order
        generator wizard.
        Use the reception date as default date for the wizard.
        Use partner_id as default supplier for the wizard.
        Use quantity of the first item received as default quantity for the
        wizard.
        """
        for transfer_details in self.browse():
            transfer_details.do_detailed_transfer()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.generator',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_date': self.picking_id.date,
                        'default_partner_id': self.picking_id.partner_id.id,
                        'default_initial_quantity': self.item_ids[0].quantity}
        }
