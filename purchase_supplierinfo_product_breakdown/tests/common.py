from odoo.tests import Form, TransactionCase


class SupplierInfoCommon(TransactionCase):
    def setUp(self):
        super(SupplierInfoCommon, self).setUp()
        self.view_name = "purchase_supplierinfo_product_breakdown.product_supplierinfo_component_form_view"  # noqa
        self.res_partner_anna = self.env.ref(
            "purchase_supplierinfo_product_breakdown.res_partner_test_demo_anna",
            raise_if_not_found=False,
        )
        self.res_partner_supplier_max = self.env.ref(
            "purchase_supplierinfo_product_breakdown.res_partner_supplier_test_demo_max",
            raise_if_not_found=False,
        )
        self.product_product_toolbox = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_product_test_demo_toolbox",
            raise_if_not_found=False,
        )
        self.product_product_component_hammer = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_product_test_demo_hammer",
            raise_if_not_found=False,
        )
        self.product_product_component_saw = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_product_test_demo_saw",
            raise_if_not_found=False,
        )
        self.product_product_component_drill = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_product_test_demo_drill",
            raise_if_not_found=False,
        )

        with Form(self.product_product_component_hammer) as form:
            with form.seller_ids.new() as seller:
                seller.name = self.res_partner_supplier_max
                seller.price = 5

        with Form(self.product_product_component_saw) as form:
            with form.seller_ids.new() as seller:
                seller.name = self.res_partner_supplier_max
                seller.price = 3.0

        with Form(self.product_product_toolbox) as form:
            with form.seller_ids.new() as seller:
                seller.name = self.res_partner_anna
                seller.price = 100.0

        self.product_supplier_info = self.product_product_toolbox.seller_ids

        with Form(self.product_supplier_info, view=self.view_name) as form:
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_hammer
                line.product_uom_qty = 5
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_saw
                line.product_uom_qty = 3
