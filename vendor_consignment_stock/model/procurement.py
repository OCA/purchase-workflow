# -*- coding: utf-8 -*-
# Author: Leonardo Pistone
# Copyright 2014 Camptocamp SA
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class Procurement(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _run(self):
        self.ensure_one()
        if self.rule_id and self.rule_id.action == 'buy_vci':
            return self.make_vci_po()
        return super(Procurement, self)._run()

    @api.multi
    def make_vci_po(self):
        """Returns a dict {procurement_id: generated_purchase_line_id}."""
        line_model = self.env['purchase.order.line']

        result = self.make_po()
        for proc in self:
            # The order line id can be False if there was an error.
            # Do nothing in that case because errors are handled in make_po().
            if proc.id in result:
                order_lines = line_model.search([
                    ('procurement_ids', 'in', [proc.id])])
                for order_line in order_lines:
                    order_line.order_id.is_vci = True
        return result

    def _make_po_select_supplier(self, suppliers):
        if self.rule_id.action == 'buy_vci':
            for supplier in suppliers:
                if supplier.name == self.move_dest_id.restrict_partner_id:
                    return supplier
        else:
            return super(Procurement, self)._make_po_select_supplier(suppliers)

    @api.multi
    def _check(self):
        self.ensure_one()
        if self.rule_id and self.rule_id.action == 'buy_vci':
            purchase = self.purchase_id
            if purchase and purchase.state in ['purchase', 'done']:
                self.move_dest_id.state = 'confirmed'
                self.move_dest_id.action_assign()
                return True
            else:
                return False
        else:
            return super(Procurement, self)._check()
