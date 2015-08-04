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


class TestProductSupplierinfoDiscount(common.TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfoDiscount, self).setUp()
        self.supplierinfo_model = self.env['product.supplierinfo']
        self.purchase_order_line_model = self.env['purchase.order.line']
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_3 = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_6')
        self.supplierinfo = self.supplierinfo_model.create(
            {'min_qty': 1,
             'name': self.partner_3.id,
             'product_tmpl_id': self.product.product_tmpl_id.id,
             'pricelist_ids': [
                 (0, 0, {'min_quantity': 1,
                         'price': 15,
                         'discount': 10}),
                 (0, 0, {'min_quantity': 10,
                         'price': 15,
                         'discount': 20}),
             ]}
        )

    def test_purchase_order_partner_3_qty_1(self):
        res = self.purchase_order_line_model.onchange_product_id(
            self.partner_3.property_product_pricelist_purchase.id,
            self.product.id, 1, self.product.uom_id.id, self.partner_3.id)
        self.assertEqual(
            res['value']['discount'], 10.0,
            "Incorrect discount for product 6 with partner 3 and qty 1")

    def test_purchase_order_partner_3_qty_10(self):
        res = self.purchase_order_line_model.onchange_product_id(
            self.partner_3.property_product_pricelist_purchase.id,
            self.product.id, 10, self.product.uom_id.id, self.partner_3.id)
        self.assertEqual(
            res['value']['discount'], 20.0,
            "Incorrect discount for product 6 with partner 3 and qty 10")

    def test_purchase_order_partner_1_qty_1(self):
        res = self.purchase_order_line_model.onchange_product_id(
            self.partner_3.property_product_pricelist_purchase.id,
            self.product.id, 1, self.product.uom_id.id, self.partner_1.id)
        self.assertEqual(
            res['value'].get('discount', 0.0), 0.0,
            "Incorrect discount for product 6 with partner 1 and qty 1")
