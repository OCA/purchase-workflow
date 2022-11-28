# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2022 Open Source Integrators - Diogo Cordeiro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form

from odoo.addons.base_revision.tests import test_base_revision


class TestPurchaseOrderRevision(test_base_revision.TestBaseRevision):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.revision_model = cls.env["purchase.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})

    @staticmethod
    def _revision_tester(tester):
        # Cancel the tester
        tester.button_cancel()
        # Create a new revision
        return tester.create_revision()

    def _create_tester(self):
        purchase_form = Form(self.revision_model)
        purchase_form.partner_id = self.partner
        with purchase_form.order_line.new() as line_form:
            line_form.product_id = self.product
        return purchase_form.save()
