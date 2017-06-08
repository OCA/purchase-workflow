# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestPurchaseAnalytic(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseAnalytic, self).setUp()

    def test_analytic_account(self):
        """ Create a purchase order with line
            Set analytic account on purchase
            Check analytic account on line is set
        """
        po = self.env['purchase.order'].create(
            {'partner_id': self.env.ref('base.res_partner_16').id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'pricelist_id': self.env.ref('purchase.list0').id
             })

        vals = self.env['purchase.order.line'].onchange_product_id(
            po.pricelist_id.id, self.env.ref('product.product_product_34').id,
            0, False, po.partner_id.id, date_order=po.date_order,
            fiscal_position_id=po.fiscal_position.id, date_planned=False,
            name=False, price_unit=False, state=po.state)
        vals['value']['order_id'] = po.id
        vals['value']['product_id'] = self.env.ref(
            'product.product_product_34').id
        po_line = self.env['purchase.order.line'].create(vals['value'])
        po.project_id = self.env.ref('account.analytic_project_1').id
        self.assertEqual(po.project_id.id,
                         self.env.ref('account.analytic_project_1').id)
        self.assertEqual(po_line.account_analytic_id.id,
                         self.env.ref('account.analytic_project_1').id)

    def test_project_id(self):
        """ Create a purchase order without line
            Set analytic account on purchase
            Check analytic account is on purchase
        """
        po = self.env['purchase.order'].new(
            {'partner_id': self.env.ref('base.res_partner_16').id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'pricelist_id': self.env.ref('purchase.list0').id,
             'project_id': self.env.ref('account.analytic_project_1').id
             })
        po._onchange_project_id()
        self.assertEqual(po.project_id.id,
                         self.env.ref('account.analytic_project_1').id)

    def _create_po(self, partner_id):
        po = self.env['purchase.order'].create(
            {'partner_id': partner_id,
             'location_id': self.env.ref('stock.stock_location_stock').id,
             'pricelist_id': self.env.ref('purchase.list0').id
             })

        vals = self.env['purchase.order.line'].onchange_product_id(
            po.pricelist_id.id, self.env.ref('product.product_product_34').id,
            0, False, po.partner_id.id, date_order=po.date_order,
            fiscal_position_id=po.fiscal_position.id, date_planned=False,
            name=False, price_unit=False, state=po.state)
        vals['value']['order_id'] = po.id
        vals['value']['product_id'] = self.env.ref(
            'product.product_product_34').id
        self.env['purchase.order.line'].create(vals['value'])
        return po

    def test_merge_po(self):
        """ Create po1 with project1
            Create po2 with project1
            Create po3 with project2
            Merge po1 with po2
            Check po1 and po2 are cancelled
            Check po4 is created with project1
            Merge po4 with po3
            Check po4 and po3 are draft
        """
        project1 = self.env.ref('account.analytic_project_1')
        project2 = self.env.ref('account.analytic_project_2')
        partner_id = self.env.ref('base.res_partner_4').id
        po1 = self._create_po(partner_id)
        po1.project_id = project1.id
        po2 = self._create_po(partner_id)
        po2.project_id = project1.id
        po3 = self._create_po(partner_id)
        po3.project_id = project2.id
        po_merge = po1 + po2
        new_order = po_merge.do_merge()
        self.assertEqual(1, len(new_order))
        old_po_id = new_order.values()[0]
        self.assertTrue(po1.id in old_po_id)
        self.assertTrue(po2.id in old_po_id)
        self.assertEqual('cancel', po1.state)
        self.assertEqual('cancel', po2.state)
        po4 = self.env['purchase.order'].browse(new_order.keys()[0])
        self.assertEqual(project1.id, po4.project_id.id)
        po_merge = po3 + po4
        new_order = po_merge.do_merge()
        self.assertEqual(0, len(new_order))
        self.assertEqual('draft', po3.state)
        self.assertEqual('draft', po4.state)
