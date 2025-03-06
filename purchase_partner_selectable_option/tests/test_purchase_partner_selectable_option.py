# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo.addons.base.tests.common import BaseCommon


class TestPurchasePartnerSelectableOption(BaseCommon):
    def test_sale_order(self):
        result = self.env["purchase.order"].get_view(
            view_id=self.env.ref("purchase.purchase_order_form").id,
            view_type="form",
        )
        doc = etree.XML(result["arch"])
        field = doc.xpath("//field[@name='partner_id']")
        domain = field[0].get("domain")
        self.assertTrue("('purchase_selectable', '=', True)" in domain)
