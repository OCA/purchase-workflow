from odoo.tests import Form, tagged

from odoo.addons.purchase_supplierinfo_product_breakdown.tests.common import (
    SupplierInfoCommon,
)


@tagged("post_install", "-at_install", "test_product_supplierinfo")
class TestSupplierInfo(SupplierInfoCommon):
    """
    TEST 1 - Check correct compute product price
    """

    def setUp(self):
        super(TestSupplierInfo, self).setUp()
        with Form(self.product_product_component_hammer) as form, form.seller_ids.edit(
            0
        ) as seller:
            seller.name = self.res_partner_anna

    # TEST 1 - Check correct compute product price
    def test_correct_product_price(self):
        """Check correct compute product price"""
        self.assertEqual(
            self.product_supplier_info.price,
            34,
            msg="Toolbox price must be equal to 34",
        )
        with Form(self.product_product_component_hammer) as form, form.seller_ids.edit(
            0
        ) as seller:
            seller.price = 10
        self.assertEqual(
            self.product_supplier_info.price,
            59,
            msg="Toolbox price must be equal to 59",
        )
        self.res_partner_anna.write({"use_product_components": False})
        self.assertEqual(
            self.product_supplier_info.price,
            100,
            msg="Toolbox price must be equal to 100",
        )
