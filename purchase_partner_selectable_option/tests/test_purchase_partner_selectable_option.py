# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.tests import common

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestPurchasePartnerSelectableOption(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

    def test_sale_order(self):
        result = self.env["purchase.order"].get_view(
            view_id=self.env.ref("purchase.purchase_order_form").id,
            view_type="form",
        )
        doc = etree.XML(result["arch"])
        field = doc.xpath("//field[@name='partner_id']")
        domain = field[0].get("domain")
        self.assertTrue("('purchase_selectable', '=', True)" in domain)
