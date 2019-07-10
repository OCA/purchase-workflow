# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

import odoo.tests.common as common
from odoo import fields


class TestPurchaseOrder(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.product_obj = cls.env['product.product']
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': cls.env.ref(
                'account.data_account_type_expenses').id
        })
        usage = cls.env['purchase.product.usage'].create({
            'name': 'Personal',
            'code': 'Ps',
            'account_id': cls.account.id
        })
        cls.usage_mis = cls.env['purchase.product.usage'].create({
            'name': 'Miscellaneous',
            'code': 'MIS',
            'account_id': cls.account.id
        })
        categ_manual = cls.env['product.category'].create({
            'name': 'Manual',
            'property_valuation': 'manual_periodic',
        })
        cls.product_1 = cls.product_obj.create({
            'name': 'Test product 1',
            'type': 'consu',
            'categ_id': categ_manual.id
        })
        cls.product_2 = cls.product_obj.create({
            'name': 'Test product 2',
            'type': 'product',
            'categ_id': categ_manual.id
        })
        cls.product_3 = cls.product_obj.create({
            'name': 'Test product 3',
            'type': 'product',
            'categ_id': categ_manual.id
        })
        cls.usage_pro = cls.env['purchase.product.usage'].create({
            'name': 'Miscellaneous',
            'code': 'MIS',
            'product_id': cls.product_3.id
        })
        cls.po_model = cls.env['purchase.order.line']
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.env.ref('base.res_partner_3').id,
        })
        cls.po_line_1 = cls.po_model.create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.product_1.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'usage_id': usage.id,
            'product_qty': 1.0,
            'product_uom': cls.product_1.uom_id.id,
            'price_unit': 10.0,
        })
        cls.po_line_2 = cls.po_model.create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.product_2.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'usage_id': usage.id,
            'product_qty': 1.0,
            'product_uom': cls.product_2.uom_id.id,
            'price_unit': 1.0,
        })
        cls.group_purchase_user = cls.env.ref('purchase.group_purchase_user')
        cls.test_user = cls.env['res.users'].create(
            {'name': 'test', 'login': 'test',
             'groups_id':
             [(6, 0, [cls.group_purchase_user.id])]})

    def test_invoice(self):
        invoice = self.env['account.invoice'].new({
            'partner_id': self.env.ref('base.res_partner_3').id,
            'purchase_id': self.purchase_order.id,
        })
        invoice.purchase_order_change()
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_1
        )
        self.assertEqual(line.account_id, self.account)
        line = invoice.invoice_line_ids.filtered(
            lambda x: x.purchase_line_id == self.po_line_2
        )
        self.assertNotEqual(line.account_id, self.account)

    def test_security(self):
        usage = self.env['purchase.product.usage'].sudo(self.test_user).search(
            [('code', '=', self.usage_mis.code)])
        #  purchase user should see all
        self.assertEqual(len(usage), 2)

    def test_name_get(self):
        name = self.po_line_1.usage_id.name_get()
        self.assertEqual(name[0][1], '[Ps] Personal')

    def test_product(self):
        pol = self.po_model.new({
            'order_id': self.purchase_order.id,
            'date_planned': fields.Datetime.now(),
            'name': 'Test',
            'product_qty': 1.0,
            'price_unit': 10.0,
        })
        pol.usage_id = self.usage_pro
        pol.onchange_usage_id()
        self.assertEqual(pol.product_id, self.product_3)
        pol.usage_id = self.usage_mis
        pol.onchange_usage_id()
        #  no product, it remains unchanged
        self.assertEqual(pol.product_id, self.product_3)
