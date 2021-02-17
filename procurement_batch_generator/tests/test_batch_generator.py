# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestProcurementBatchGenerator(TransactionCase):
    def test_wizard(self):
        """Create procurement requests, validate and check result"""
        pbgo = self.env["procurement.batch.generator"]
        ctx = self.env.context.copy()
        ctx.update(
            {
                "active_ids": [
                    self.env.ref("product.product_product_9").id,
                    self.env.ref("product.product_product_12").id,
                ],
                "active_model": "product.product",
            }
        )
        wiz = pbgo.with_context(ctx).create({})
        wiz.line_ids.write({"procurement_qty": 42})
        action = wiz.validate()
