# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestSubcontractedService(TransactionCase):
    def setUp(self):
        super(TestSubcontractedService, self).setUp()
        # 1. find a supplier
        self.supplier = self.env.ref('base.res_partner_1')

        # 2. create a service product unconfigured
        values = {'name': 'Service Subcontracted',
                  'type': 'service',
                  'seller_ids': [(0, 0, {
                      'name': self.supplier.id,
                      'price': 100.0,
                  })]
                  }
        self.pdt_service = self.env['product.product'].create(values)
        # 3. create procurement rules in companies
        companies = self.env['res.company'].search([])
        companies._set_subcontracting_service_proc_rule()

        # 4. find a customer
        self.customer = self.env['res.partner'].search(
            [('customer', '=', True)],
            limit=1
        )

    def test_01_product_no_configured(self):
        # create a SO
        so_vals = {
            'partner_id': self.customer.id,
            'partner_invoice_id': self.customer.id,
            'partner_shipping_id': self.customer.id,
            'order_line': [(0, 0, {
                'name': self.pdt_service.name,
                'product_id': self.pdt_service.id,
                'product_uom_qty': 1,
                'product_uom': self.pdt_service.uom_id.id,
                'price_unit': self.pdt_service.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        so = self.env['sale.order'].create(so_vals)
        # confirm SO
        so.action_confirm()
        # check NO procurement exists for the SO
        self.assertFalse(so.procurement_group_id)

    def test_02_product_configured(self):
        # 1. configure product
        self.pdt_service.property_subcontracted_service = True

        # create a SO
        so_vals = {
            'partner_id': self.customer.id,
            'partner_invoice_id': self.customer.id,
            'partner_shipping_id': self.customer.id,
            'order_line': [(0, 0, {
                'name': self.pdt_service.name,
                'product_id': self.pdt_service.id,
                'product_uom_qty': 1,
                'product_uom': self.pdt_service.uom_id.id,
                'price_unit': self.pdt_service.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        so = self.env['sale.order'].create(so_vals)

        # confirm SO
        so.action_confirm()

        # check a procurement exists for the SO
        self.assertTrue(so.procurement_group_id)

        # check a PO has been created with the product and the supplier
        # defined in product's supplierinfo
        proc = self.env['procurement.order'].search(
            [('sale_line_id', 'in', [so.order_line.ids])]
        )
        self.assertTrue(proc.purchase_id)
        self.assertIn(self.pdt_service,
                      proc.purchase_id.order_line.mapped('product_id'))
