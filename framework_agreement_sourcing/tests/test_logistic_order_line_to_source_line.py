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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from ..model.logistic_requisition_source import AGR_PROC
from .common import CommonSourcingSetUp


class TestTransformation(CommonSourcingSetUp):

    def test_01_enough_qty_on_first_agr(self):
        """Test that we can source a line with one agreement and low qty"""
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
        to_validate_ids = self.requisition_line_model._generate_source_line(cr, uid, agr_line)
        self.assertTrue(len(to_validate_ids) == 1)
        to_validate = self.source_line_model.browse(cr, uid, to_validate_ids[0])
        self.assertEqual(to_validate.procurement_method, AGR_PROC)
        self.assertEqual(to_validate.unit_cost, 50)
        self.assertEqual(to_validate.proposed_qty, 400)

    def test_02_enough_qty_on_high_agr(self):
        """Test that we can source a line correctly on both agreement"""
        cr, uid = self.cr, self.uid
        lines = self.requisition.line_ids
        agr_line = None
        for line in lines:
            if line.product_id == self.cheap_on_high_agreement.product_id:
                agr_line = line
                break
        self.assertTrue(agr_line)
        agr_line.write({'requested_qty': 1500})
        agr_line.refresh()
        to_validate_ids = self.requisition_line_model._generate_source_line(cr, uid, agr_line)
        self.assertTrue(len(to_validate_ids) == 1)
        to_validate = self.source_line_model.browse(cr, uid, to_validate_ids[0])
        self.assertEqual(to_validate.procurement_method, AGR_PROC)
        self.assertEqual(to_validate.unit_cost, 30)
        self.assertEqual(to_validate.proposed_qty, 1500)

    def test_03_not_enough_qty_on_high_agreement(self):
        """Test that we can source a line with one agreement and high qty"""
        cr, uid = self.cr, self.uid
        lines = self.requisition.line_ids
        agr_line = None
        for line in lines:
            if line.product_id == self.cheap_on_high_agreement.product_id:
                agr_line = line
                break
        self.assertTrue(agr_line)
        agr_line.write({'requested_qty': 2400})
        agr_line.refresh()
        to_validate_ids = self.requisition_line_model._generate_source_line(cr, uid, agr_line)
        self.assertTrue(len(to_validate_ids) == 2)
        # We validate generated line
        to_validates = self.source_line_model.browse(cr, uid, to_validate_ids)
        # high_line
        # idiom taken from Python cookbook
        high_line = next((x for x in to_validates
                              if x.framework_agreement_id == self.cheap_on_high_agreement), None)
        self.assertTrue(high_line, msg="High agreement was not used")
        self.assertEqual(high_line.procurement_method, AGR_PROC)
        self.assertEqual(high_line.proposed_qty, 2000)
        self.assertEqual(high_line.unit_cost, 30)

        # low_line
        low_line = next((x for x in to_validates
                              if x.framework_agreement_id == self.cheap_on_low_agreement), None)
        self.assertTrue(low_line, msg="Low agreement was not used")
        self.assertEqual(low_line.procurement_method, AGR_PROC)
        self.assertEqual(low_line.proposed_qty, 400)
        self.assertEqual(low_line.unit_cost, 50)


    def test_03_not_enough_qty_on_all_agreemenst(self):
        """Test that we """
        cr, uid = self.cr, self.uid
        lines = self.requisition.line_ids
        agr_line = None
        for line in lines:
            if line.product_id == self.cheap_on_high_agreement.product_id:
                agr_line = line
                break
        self.assertTrue(agr_line)
        agr_line.write({'requested_qty': 5000})
        agr_line.refresh()
        to_validate_ids = self.requisition_line_model._generate_source_line(cr, uid, agr_line)
        self.assertTrue(len(to_validate_ids) == 3)
        # We validate generated line
        to_validates = self.source_line_model.browse(cr, uid, to_validate_ids)
        # high_line
        # idiom taken from Python cookbook
        high_line = next((x for x in to_validates
                              if x.framework_agreement_id == self.cheap_on_high_agreement), None)
        self.assertTrue(high_line, msg="High agreement was not used")
        self.assertEqual(high_line.procurement_method, AGR_PROC)
        self.assertEqual(high_line.proposed_qty, 2000)
        self.assertEqual(high_line.unit_cost, 30)

        # low_line
        low_line = next((x for x in to_validates
                              if x.framework_agreement_id == self.cheap_on_low_agreement), None)
        self.assertTrue(low_line, msg="Low agreement was not used")
        self.assertEqual(low_line.procurement_method, AGR_PROC)
        self.assertEqual(low_line.proposed_qty, 1200)
        self.assertEqual(low_line.unit_cost, 45)

        # Tender line
        tender_line = next((x for x in to_validates
                                if not x.framework_agreement_id), None)
        self.assertTrue(tender_line, msg="Tender line was not generated")
        self.assertNotEqual(tender_line.procurement_method, AGR_PROC)
