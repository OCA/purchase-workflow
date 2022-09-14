from odoo.tests import Form, tagged

from odoo.addons.purchase_supplierinfo_product_breakdown.tests.common import (
    SupplierInfoCommon,
)


@tagged("post_install", "-at_install", "test_product_supplierinfo_component")
class TestProductSupplierInfoComponent(SupplierInfoCommon):
    """
    TEST 1 - Component current price compute is correct
    TEST 2 - Component price total compute is correct
    TEST 3 - Compute supplier by product and partner
    """

    def setUp(self):
        super(TestProductSupplierInfoComponent, self).setUp()
        with Form(self.product_product_component_hammer) as form, form.seller_ids.edit(
            0
        ) as seller:
            seller.name = self.res_partner_anna

        with Form(self.product_product_component_saw) as form, form.seller_ids.edit(
            0
        ) as seller:
            seller.name = self.res_partner_anna

    # TEST 1 - Component current price compute is correct
    def test_check_correct_component_current_price(self):
        """Component current price compute is correct"""
        component_hammer, component_saw = self.product_supplier_info.component_ids
        self.assertEqual(
            component_hammer.current_price,
            5,
            msg="Hammer current price must be equal to 5",
        )
        with Form(self.product_product_component_hammer) as form, form.seller_ids.edit(
            0
        ) as line:
            line.price = 10
        self.assertEqual(
            component_hammer.current_price,
            10,
            msg="Hammer current price must be equal to 10",
        )
        with Form(self.product_product_component_hammer) as form, form.seller_ids.edit(
            0
        ) as line:
            line.price = 0
        self.assertEqual(
            component_hammer.current_price,
            5,
            msg="Hammer current price must be equal to 5",
        )
        self.assertEqual(
            component_saw.current_price, 3, msg="Saw current price must be equal to 3"
        )
        with Form(self.product_product_component_saw) as form, form.seller_ids.edit(
            0
        ) as line:
            line.price = 24
        self.assertEqual(
            component_saw.current_price, 24, msg="Saw current price must be equal to 24"
        )
        with Form(self.product_product_component_saw) as form, form.seller_ids.edit(
            0
        ) as line:
            line.price = 0
        self.assertEqual(
            component_saw.current_price, 3, msg="Saw current price must be equal to 3"
        )

    # TEST 2 - Component price total compute is correct
    def test_check_correct_component_price_total(self):
        """Component price total compute is correct"""
        component_hammer, component_saw = self.product_supplier_info.component_ids
        self.assertEqual(
            component_hammer.price_total,
            25,
            msg="Hammer price total must be equal to 25",
        )
        self.assertEqual(
            component_saw.price_total, 9, msg="Saw price total must be equal to 9"
        )
        with Form(self.product_product_component_hammer) as form, form.seller_ids.edit(
            0
        ) as line:
            line.price = 10
        self.assertEqual(
            component_hammer.price_total,
            50,
            msg="Hammer price total must be equal to 50",
        )
        with Form(self.product_product_component_saw) as form, form.seller_ids.edit(
            0
        ) as line:
            line.price = 6
        self.assertEqual(
            component_saw.price_total, 18, msg="Saw price total must be equal to 18"
        )

    # TEST - Compute supplier by product and partner
    def test_component_supplier(self):
        """Compute supplier by product and partner"""
        SupplierInfoComponent = self.env["product.supplierinfo.component"]

        supplier_empty = SupplierInfoComponent.get_supplier_by_args(
            self.product_product_component_hammer.product_tmpl_id.id,
            self.res_partner_supplier_max.id,
        ).name
        self.assertFalse(supplier_empty, msg="Recordset must be empty")
        supplier_valid = SupplierInfoComponent.get_supplier_by_args(
            self.product_product_component_hammer.product_tmpl_id.id,
            self.res_partner_anna.id,
        ).name
        self.assertEqual(
            supplier_valid,
            self.res_partner_anna,
            msg="Supplier must be equal to 'Anna' supplier",
        )
        with Form(self.product_product_component_hammer) as form, form.seller_ids.edit(
            0
        ) as seller:
            seller.name = self.res_partner_supplier_max
        supplier_empty = SupplierInfoComponent.get_supplier_by_args(
            self.product_product_component_hammer.product_tmpl_id.id,
            self.res_partner_anna.id,
        ).name
        self.assertFalse(supplier_empty, msg="Recordset must be empty")
        supplier_valid = SupplierInfoComponent.get_supplier_by_args(
            self.product_product_component_hammer.product_tmpl_id.id,
            self.res_partner_supplier_max.id,
        ).name
        self.assertEqual(
            supplier_valid,
            self.res_partner_supplier_max,
            msg="Supplier must be equal to 'Max' supplier",
        )
