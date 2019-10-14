# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def get_domain_draft_purchase_order(self, supplier_id):
        domain = [
            ('partner_id', '=', supplier_id),
            ('state', '=', 'draft'),
            ('picking_type_id', '=', self.picking_type_id.id),
            ('company_id', '=', self.company_id.id),
        ]

        return domain


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def change_supplier(self, supplier_id):
        purchase_obj = self.env['purchase.order']

        first_line = self[0]
        original_order = first_line.order_id

        # search for already existing purchase order to add new products or
        # create a new purchase order with supplier_id
        domain = original_order.get_domain_draft_purchase_order(supplier_id)
        purchase_orders = purchase_obj.search(domain)
        if purchase_orders:
            quotation_purchase_order = purchase_orders[0]
        else:
            group_id =\
                (first_line.sale_ids and
                 first_line.sale_ids[0].procurement_group_id and
                 first_line.sale_ids[0].procurement_group_id.id) or False
            quotation_purchase_order = purchase_obj.create({
                'partner_id': supplier_id,
                'group_id': group_id,
            })

        self.write({'order_id': quotation_purchase_order.id})

        return quotation_purchase_order.id
