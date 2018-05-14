# Copyright 2018 Open Source Integrators
#   (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
from odoo.tests import common


class TestLandedCostCompanyPercentage(common.TransactionCase):

    def setUp(self):
        super(TestLandedCostCompanyPercentage, self).setUp()

        # Refs
        self.group_stock_manager = self.env.ref('stock.group_stock_manager')
        self.group_purchase_manager = self.env.ref(
            'purchase.group_purchase_manager')
        self.company1 = self.env.ref('base.main_company')
        self.partner_id = self.env.ref('base.res_partner_1')
        self.product_uom = self.env.ref('product.product_uom_unit')

        # Get required Model
        self.product_model = self.env['product.product']
        self.purchase_model = self.env['purchase.order']
        self.purchase_line_model = self.env['purchase.order.line']
        self.user_model = self.env['res.users']
        self.product_ctg_model = self.env['product.category']
        self.journal_model = self.env['account.journal']
        self.landed_cost_model = self.env['stock.landed.cost']

        # Create users
        self.user = self._create_user('user_1',
                                      [self.group_stock_manager,
                                       self.group_purchase_manager],
                                      self.company1)

        # Create Product category and Products
        self.product_ctg = self._create_product_category()
        self.product = self._create_product()
        self.transportation_product = self._create_transportation_product()

        # Create landed cost journal
        self.journal = self._create_journal()

        # Prepare purchase order values
        self.po_vals = {
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_qty': 5.0,
                    'product_uom': self.product.uom_po_id.id,
                    'price_unit': 100.0,
                    'date_planned': datetime.today().strftime(DF),
                })],
        }
        # Update company record with landed costs information
        self.company1.write({'landed_cost_journal_id': self.journal.id,
                             'landed_cost_company_line': [(0, 0, {
                                 'product_id': self.transportation_product.id,
                                 'percentage': 5.0})]})

    def _create_journal(self):
        journal = self.journal_model.create(
            {'name': 'Landed Cost Journal', 'type': 'general',
             'code': 'LCJ13'})
        return journal

    def _create_user(self, login, groups, company):
        """ Create a user."""
        group_ids = [group.id for group in groups]
        user = \
            self.user_model.with_context({'no_reset_password': True}).create({
                'name': 'Test User',
                'login': login,
                'password': 'demo',
                'email': 'test@yourcompany.com',
                'company_id': company.id,
                'company_ids': [(4, company.id)],
                'groups_id': [(6, 0, group_ids)]
            })
        return user

    def _create_product_category(self):
        """Create a Product Category."""
        product_ctg = self.product_ctg_model.create({
            'name': 'FIFO',
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time'
        })
        return product_ctg

    def _create_product(self):
        """Create a Product."""
        product = self.product_model.create({
            'name': 'Test Product',
            'categ_id': self.product_ctg.id,
            'type': 'product',
            'uom_id': self.product_uom.id,
        })
        return product

    def _create_transportation_product(self):
        """Create a Transportation Product."""
        product = self.product_model.create({
            'name': 'Transportation',
            'categ_id': self.product_ctg.id,
            'type': 'service',
            'uom_id': self.product_uom.id,
            'landed_cost_ok': True,
            'split_method': 'equal'
        })
        return product

    def test_purchase_order_company_landed_cost_percentage(self):
        """Test purchase order and create landed cost on receive picking"""

        # Create purchase order
        self.po = self.purchase_model.create(self.po_vals)
        self.assertTrue(self.po, 'Purchase: no purchase order created')

        # Confirm purchase order
        self.po.button_confirm()

        self.assertEqual(self.po.picking_count, 1,
                         'Purchase: one picking should be created"')
        self.picking = self.po.picking_ids[0]
        self.picking.force_assign()
        self.picking.move_line_ids.write({'qty_done': 5.0})
        self.picking.with_context(
            test_stock_landed_cost_company_percentage=True
        ).button_validate()

        landed_cost_record = self.landed_cost_model.search(
            [('picking_ids', '=', self.picking.id)])
        self.assertEqual(len(landed_cost_record), 1)
        self.assertEqual(len(landed_cost_record.cost_lines), 1)
        self.assertEqual(landed_cost_record.cost_lines[0].price_unit, 25)
        self.assertEqual(len(landed_cost_record.valuation_adjustment_lines), 1)
        self.assertEqual(landed_cost_record.valuation_adjustment_lines[0].additional_landed_cost, 25) # noqa
        self.assertEqual(len(landed_cost_record.valuation_adjustment_lines), 1)
        self.assertEqual(landed_cost_record.account_move_id.state, 'posted')
