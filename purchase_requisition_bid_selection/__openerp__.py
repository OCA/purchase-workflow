# -*- coding: utf-8 -*-
#    Copyright 2013-2015 Camptocamp SA
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

{"name": "Purchase Requisition Bid Selection",
 "version": "8.0.2.1.0",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "license": "AGPL-3",
 "category": "Purchase Management",
 "complexity": "normal",
 "images": [],
 "depends": ["purchase_requisition",
             "stock",  # For incoterms
             "purchase_rfq_bid_workflow",
             "purchase_requisition_multicurrency",
             ],
 "demo": [],
 "data": ["wizard/modal.xml",
          "wizard/purchase_requisition_partner_view.xml",
          "wizard/update_bid_internal_remark.xml",
          "wizard/update_remark.xml",
          "view/purchase_requisition.xml",
          "view/purchase_order.xml",
          "view/report_purchaserequisition.xml",
          "report.xml",
          "workflow/purchase_order.xml",
          "workflow/purchase_requisition.xml",
          "data/purchase.cancelreason.yml",
          ],
 "auto_install": False,
 "test": ["test/process/restricted.yml",
          ],
 "installable": True,
 "certificate": "",
 }
