# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api
from odoo.addons.purchase_requisition.models.purchase_requisition import PurchaseOrder


def post_load_hook():

    @api.multi
    def new_write(self, vals):
        return super(PurchaseOrder, self).write(vals)

    if not hasattr(PurchaseOrder, 'write_original'):
        PurchaseOrder.write_original = PurchaseOrder.write

    PurchaseOrder.write = new_write
