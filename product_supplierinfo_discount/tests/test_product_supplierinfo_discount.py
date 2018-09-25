# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#        Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import TransactionCase
from odoo import fields


class TestProductSupplierinfoDiscount(TransactionCase):

    def setUp(self):
        super(TestProductSupplierinfoDiscount, self).setUp()
        self.supplierinfo_model = self.env['product.supplierinfo']
        self.purchase_order_line_model = self.env['purchase.order.line']
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_3 = self.env.ref('base.res_partner_3')
        self.product = self.env.ref('product.product_product_6')
        self.supplierinfo = self.supplierinfo_model.create({
            'min_qty': 0.0,
            'name': self.partner_3.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'discount': 10,
        })
        self.supplierinfo2 = self.supplierinfo_model.create({
            'min_qty': 10.0,
            'name': self.partner_3.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'discount': 20,
        })
        self.purchase_order = self.env['purchase.order'].create(
            {'partner_id': self.partner_3.id})
        self.po_line_1 = self.purchase_order_line_model.create(
            {'order_id': self.purchase_order.id,
             'product_id': self.product.id,
             'date_planned': fields.Datetime.now(),
             'name': 'Test',
             'product_qty': 1.0,
             'product_uom': self.env.ref('product.product_uom_categ_unit').id,
             'price_unit': 10.0})

    def test_001_purchase_order_partner_3_qty_1(self):
        self.po_line_1._onchange_quantity()
        self.assertEquals(
            self.po_line_1.discount, 10,
            "Incorrect discount for product 6 with partner 3 and qty 1: "
            "Should be 10%")

    def test_002_purchase_order_partner_3_qty_10(self):
        self.po_line_1.write({'product_qty': 10})
        self.po_line_1._onchange_quantity()
        self.assertEquals(
            self.po_line_1.discount, 20.0,
            "Incorrect discount for product 6 with partner 3 and qty 10: "
            "Should be 20%")

    def test_003_purchase_order_partner_1_qty_1(self):
        self.po_line_1.write({
            'partner_id': self.partner_1.id,
            'product_qty': 1,
        })
        self.po_line_1.onchange_product_id()
        self.assertEquals(
            self.po_line_1.discount, 0.0, "Incorrect discount for product "
            "6 with partner 1 and qty 1")

    def test_004_prepare_purchase_order_line(self):
        procurement_rule = self.env['procurement.rule'].create({
            'sequence': 20,
            'location_id': self.env.ref('stock.stock_location_locations').id,
            'picking_type_id': self.env.ref('stock.chi_picking_type_in').id,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'propagate': True,
            'procure_method': 'make_to_stock',
            'route_sequence': 5.0,
            'name': 'YourCompany:  Buy',
            'route_id': self.env.ref('stock.route_warehouse0_mto').id,
            'action': 'buy',
        })
        po_line_vals = {
            'origin': 'SO012:WH: Stock -> Customers MTO',
            'product_uom': self.env.ref('product.product_uom_unit').id,
            'product_qty': 50,
            'location_id': self.env.ref('stock.stock_location_locations').id,
            'company_id': self.env.ref('base.main_company').id,
            'state': 'confirmed',
            'warehouse_id': self.env.ref('stock.warehouse0').id,
            'move_dest_id': self.env.ref('stock.stock_location_customers').id,
            'message_unread_counter': 0,
            'name': 'WH: Stock -> Customers MTO',
            'product_id': self.product.id,
            'date_planned': fields.Datetime.now(),
            'rule_id': procurement_rule.id,
        }
        res = procurement_rule._prepare_purchase_order_line(
            self.product, 50, self.env.ref('product.product_uom_unit'),
            po_line_vals, self.purchase_order, self.supplierinfo,
        )
        self.assertTrue(res.get('discount'), 'Should have a discount key')

    def test_005_default_supplierinfo_discount(self):
        # Create an original supplierinfo
        supplierinfo = self.supplierinfo_model.create({
            'min_qty': 0.0,
            'name': self.partner_3.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'discount': 10,
        })
        # Change the partner and raise onchange function
        self.partner_1.default_supplierinfo_discount = 15
        supplierinfo.name = self.partner_1
        supplierinfo.onchange_name()
        self.assertEquals(
            supplierinfo.discount, 15, "Incorrect discount for supplierinfo "
            " after changing partner that has default discount defined.")

    def test_006_supplierinfo_from_purchaseorder(self):
        """ Include discount when creating new sellers for a product """
        partner = self.env.ref('base.res_partner_3')
        product = self.env.ref('product.product_product_8')
        self.assertFalse(
            self.supplierinfo_model.search([
                ('name', '=', partner.id),
                ('product_tmpl_id', '=', product.product_tmpl_id.id)]))
        order = self.env['purchase.order'].create({
            'partner_id': partner.id,
        })
        self.purchase_order_line_model.create({
            'date_planned': fields.Datetime.now(),
            'discount': 40,
            'name': product.name,
            'price_unit': 10.0,
            'product_id': product.id,
            'product_qty': 1.0,
            'product_uom': product.uom_po_id.id,
            'order_id': order.id,
        })
        order.button_confirm()
        seller = self.supplierinfo_model.search([
            ('name', '=', partner.id),
            ('product_tmpl_id', '=', product.product_tmpl_id.id)])
        self.assertTrue(seller)
        self.assertEqual(seller.discount, 40)
