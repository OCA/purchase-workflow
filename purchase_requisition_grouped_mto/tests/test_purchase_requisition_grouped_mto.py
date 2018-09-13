# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestPurchaseRequisitionGoupedMto(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        buy_route = cls.env.ref('purchase.route_warehouse0_buy')
        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'Base Warehouse',
            'reception_steps': 'one_step',
            'delivery_steps': 'ship_only',
            'code': 'BWH'})

        cls.purchase_requisition_type =\
            cls.env['purchase.requisition.type'].create({
                'name': 'test type',
            })

        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'type': 'product',
            'purchase_requisition': 'tenders',
            'purchase_requisition_group_id': cls.purchase_requisition_type.id,
            'route_ids': [(6, 0, buy_route.ids)],
        })
        cls.product2 = cls.env['product.product'].create({
            'name': 'test - 2',
            'type': 'product',
            'purchase_requisition': 'tenders',
            'purchase_requisition_group_id': cls.purchase_requisition_type.id,
            'route_ids': [(6, 0, buy_route.ids)],
        })

    def test_procurement_grouping(self):
        ProcurementGroup = self.env['procurement.group']
        ProcurementGroup.run(
            self.product,
            14,
            self.env.ref('product.product_uom_unit'),
            self.warehouse_1.lot_stock_id, '/', '/', {
                'warehouse_id': self.warehouse_1,
            }
        )
        purchase_requisition = self.env['purchase.requisition'].search([
            ('type_id', '=', self.purchase_requisition_type.id),
        ])
        self.assertEqual(len(purchase_requisition.line_ids), 1)
        ProcurementGroup.run(
            self.product2,
            14,
            self.env.ref('product.product_uom_unit'),
            self.warehouse_1.lot_stock_id, '/', '/', {
                'warehouse_id': self.warehouse_1,
            }
        )
        purchase_requisition = self.env['purchase.requisition'].search([
            ('type_id', '=', self.purchase_requisition_type.id),
        ])
        self.assertEqual(len(purchase_requisition.line_ids), 2)
