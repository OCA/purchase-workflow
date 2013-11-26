# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
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
from .common import CommonSourcingSetUp


class TestSourceToPo(CommonSourcingSetUp):

    def setUp(self):
        # we generate a source line
        super(TestSourceToPo, self).setUp()
        cr, uid = self.cr, self.uid
        lines = self.requisition.line_ids
        agr_line = None
        for line in lines:
            if line.product_id == self.cheap_on_low_agreement.product_id:
                agr_line = line
                break
        self.assertTrue(agr_line)
        agr_line.write({'requested_qty': 400})
        agr_line.refresh()
        source_ids = self.requisition_line_model._generate_source_line(cr, uid, agr_line)
        self.assertTrue(len(source_ids) == 1)
        self.source_line = self.source_line_model.browse(cr, uid, source_ids[0])

    def test_01_transform_source_to_agreement(self):
        """Test transformation of an agreement source line into PO"""
        cr, uid = self.cr, self.uid
        self.assertTrue(self.source_line)
        plist = self.source_line.framework_agreement_id.supplier_id.property_product_pricelist_purchase
        self.source_line.write({'purchase_pricelist_id': plist.id})
        self.source_line.refresh()
        po_id = self.source_line_model._make_po_from_source_line(cr, uid,
                                                                 self.source_line)
        self.assertTrue(po_id)
        supplier = self.source_line.framework_agreement_id.supplier_id
        add = self.source_line.requisition_id.consignee_shipping_id
        consignee = self.source_line.requisition_id.consignee_id
        po = self.registry('purchase.order').browse(cr, uid, po_id)
        date_order = self.source_line.requisition_id.date
        date_delivery = self.source_line.requisition_id.date_delivery
        self.assertEqual(po.partner_id, supplier)
        self.assertEqual(po.pricelist_id, supplier.property_product_pricelist_purchase)
        self.assertEqual(po.date_order, date_order)
        self.assertEqual(po.dest_address_id, add)
        self.assertEqual(po.consignee_id, consignee)

        self.assertEqual(len(po.order_line), 1)
        po_line = po.order_line[0]
        self.assertEqual(po_line.product_qty, self.source_line.proposed_qty)
        self.assertEqual(po_line.product_id, self.source_line.proposed_product_id)
        self.assertEqual(po_line.product_qty, self.source_line.proposed_qty)
        self.assertEqual(po_line.product_uom, self.source_line.proposed_uom_id)
        self.assertEqual(po_line.price_unit, 50.0)
        self.assertEqual(po_line.lr_source_line_id, self.source_line)
        self.assertEqual(po_line.date_planned, date_delivery)
