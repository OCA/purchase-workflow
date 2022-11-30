from odoo.tests import Form, TransactionCase


class PurchaseTransactionCase(TransactionCase):
    def setUp(self):
        super(PurchaseTransactionCase, self).setUp()
        PurchaseOrder = self.env["purchase.order"]
        self.component_view = "purchase_vendor_bill_breakdown.purchase_order_line_components_form_view"  # noqa
        self.view_name = "purchase_supplierinfo_product_breakdown.product_supplierinfo_component_form_view"  # noqa

        self.supplier_partner = self.env.ref(
            "purchase_vendor_bill_breakdown.res_partner_supplier_test_demo_bbc",
            raise_if_not_found=False,
        )
        self.res_partner_test = self.env.ref(
            "purchase_vendor_bill_breakdown.res_partner_test_demo_oleg",
            raise_if_not_found=False,
        )
        self.res_partner_test_use_product_components = self.env.ref(
            "purchase_supplierinfo_product_breakdown.res_partner_test_demo_anna",
            raise_if_not_found=False,
        )
        self.res_partner_test_not_supplier = self.env.ref(
            "purchase_vendor_bill_breakdown.res_partner_test_demo_petya",
            raise_if_not_found=False,
        )
        self.res_partner_supplier = self.env.ref(
            "purchase_supplierinfo_product_breakdown.res_partner_supplier_test_demo_max",
            raise_if_not_found=False,
        )
        self.res_partner_supplier_2 = self.env.ref(
            "purchase_vendor_bill_breakdown.res_partner_supplier_test_demo_mts",
            raise_if_not_found=False,
        )

        self.product_product_test_1 = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_product_test_demo_toolbox",
            raise_if_not_found=False,
        )
        self.product_product_test_2 = self.env.ref(
            "purchase_vendor_bill_breakdown.product_product_test_demo_tools",
            raise_if_not_found=False,
        )
        self.product_product_component_test_1 = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_product_test_demo_hammer",
            raise_if_not_found=False,
        )
        self.product_product_component_test_2 = self.env.ref(
            "purchase_supplierinfo_product_breakdown.product_product_test_demo_saw",
            raise_if_not_found=False,
        )

        self.product_product_test_3 = self.env.ref(
            "purchase_vendor_bill_breakdown.product_product_test_demo_vegetables",
            raise_if_not_found=False,
        )

        self.product_product_component_test_3 = self.env.ref(
            "purchase_vendor_bill_breakdown.product_product_test_demo_carrot",
            raise_if_not_found=False,
        )

        self.product_product_component_test_4 = self.env.ref(
            "purchase_vendor_bill_breakdown.product_product_test_demo_potato",
            raise_if_not_found=False,
        )

        self.product_product_component_test_5 = self.env.ref(
            "purchase_vendor_bill_breakdown.product_product_test_demo_tomato",
            raise_if_not_found=False,
        )

        form = Form(PurchaseOrder)
        form.partner_id = self.res_partner_test_use_product_components
        self.purchase_order_test_1 = form.save()

        form = Form(PurchaseOrder)
        form.partner_id = self.res_partner_test
        self.purchase_order_test_2 = form.save()

        with Form(self.product_product_component_test_1) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_supplier
                line.price = 5.0
            with form.seller_ids.new() as line:
                line.name = self.res_partner_supplier_2
                line.price = 6.0

        with Form(self.product_product_component_test_2) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_supplier
                line.price = 3.0

        with Form(self.product_product_test_1) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_test_use_product_components
                line.price = 100

        self.product_supplier_info = self.product_product_test_1.seller_ids[0]

        with Form(self.product_supplier_info, view=self.view_name) as form:
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_1
                line.product_uom_qty = 5.0
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_2
                line.product_uom_qty = 3.0

        with Form(self.product_product_component_test_3) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_supplier
                line.price = 1.0

        with Form(self.product_product_component_test_4) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_supplier
                line.price = 5.0

        with Form(self.product_product_component_test_5) as form:
            with form.seller_ids.new() as line:
                line.name = self.res_partner_supplier
                line.price = 6.0

        with Form(self.product_product_test_3) as form:
            with form.seller_ids.new() as line:
                line.name = self.supplier_partner
                line.price = 100

        seller_id = self.product_product_test_3.seller_ids[0]
        with Form(seller_id, view=self.view_name) as form:
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_3
                line.product_uom_qty = 3.0
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_4
                line.product_uom_qty = 4.0
            with form.component_ids.new() as line:
                line.component_id = self.product_product_component_test_5
                line.product_uom_qty = 5.0

        form = Form(PurchaseOrder)
        form.partner_id = self.res_partner_test_use_product_components
        form.use_product_components = False
        with form.order_line.new() as line:
            line.product_id = self.product_product_test_1
            line.price_unit = 1.0
            line.product_qty = 1.0
        self.purchase_order_without_components = form.save()
