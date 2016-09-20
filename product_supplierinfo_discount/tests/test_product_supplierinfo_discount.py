##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import openerp.tests.common as common
import time


class TestProductSupplierinfoDiscount(common.TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfoDiscount, self).setUp()
        self.supplierinfo_model = self.env['product.supplierinfo']
        self.purchase_order_line_model = self.env['purchase.order.line']
        self.purchase_order_model = self.env['purchase.order']
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_3 = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_6')
        self.supplierinfo1 = self.supplierinfo_model.create(
            {'min_qty': 1,
             'name': self.partner_3.id,
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'price': 15,
             'discount': 10})
        self.supplierinfo2 = self.supplierinfo_model.create(
            {'min_qty': 10,
             'name': self.partner_3.id,
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'price': 15,
             'discount': 20})
        self.purchase_order1 = self.purchase_order_model.create(
            {'name': 'Order1',
             'partner_id': self.partner_1.id, })
        self.purchase_order2 = self.purchase_order_model.create(
            {'name': 'Order2',
             'partner_id': self.partner_3.id, })

    def test_purchase_order_partner_3_qty_1(self):
        pol1 = self.purchase_order_line_model.create(
            {'name': 'line1',
             'product_id': self.product.id,
             'product_qty': 1,
             'price_unit': 10,
             'product_uom': self.product.uom_id.id,
             'partner_id': self.partner_3.id,
             'order_id': self.purchase_order2.id,
             'date_planned': time.strftime('%Y-%m-%d')})
        pol1.onchange_pol_info()
        self.assertEqual(
            pol1.discount, 10.0,
            "Incorrect discount for product 6 with partner 3 and qty 1")

    def test_purchase_order_partner_3_qty_10(self):
        pol2 = self.purchase_order_line_model.create(
            {'name': 'line2',
             'product_id': self.product.id,
             'product_qty': 10,
             'price_unit': 10,
             'product_uom': self.product.uom_id.id,
             'partner_id': self.partner_3.id,
             'order_id': self.purchase_order2.id,
             'date_planned': time.strftime('%Y-%m-%d')})
        pol2.onchange_pol_info()
        self.assertEqual(
            pol2.discount, 20.0,
            "Incorrect discount for product 6 with partner 3 and qty 10")

    def test_purchase_order_partner_1_qty_1(self):
        pol3 = self.purchase_order_line_model.create(
            {'name': 'line3',
             'product_id': self.product.id,
             'product_qty': 1,
             'price_unit': 10,
             'product_uom': self.product.uom_id.id,
             'partner_id': self.partner_1.id,
             'order_id': self.purchase_order1.id,
             'date_planned': time.strftime('%Y-%m-%d')})
        pol3.onchange_pol_info()
        self.assertEqual(
            pol3.discount, 0.0,
            "Incorrect discount for product 6 with partner 1 and qty 1")
