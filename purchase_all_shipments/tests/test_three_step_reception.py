#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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
from openerp.tests import common


class TestThreeStepReception(common.TransactionCase):

    def test_three_steps_generate_three_pickings(self):
        wh = self.env.ref('stock.warehouse0')
        wh.reception_steps = 'three_steps'
        po = self.env.ref('purchase.purchase_order_1')
        po.location_id = wh.wh_input_stock_loc_id
        po.signal_workflow('purchase_confirm')

        self.assertEqual(1, po.shipment_count)
        self.assertEqual(3, po.all_shipment_count)
