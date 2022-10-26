# Copyright 2021 Akretion - www.akretion.com.br -
# @author  Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class PurchaseAddProductsFromBoMTest(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.purchase_order = cls.env['purchase.order']
        cls.add_product_from_bom_wizard = \
            cls.env["add.products.from.bom"]
        cls.product = cls.env.ref('product.product_product_3')
        cls.product_bom = cls.env.ref('mrp.mrp_bom_manufacture')
        cls.env.ref('mrp.mrp_bom_manufacture')

        # Include Products with BoM Type Phanton, Normal and with two BoM
        cls.product_bom.bom_line_ids.create([{
            'product_id': cls.env.ref('mrp.product_product_table_kit').id,
            'product_qty': 1,
            'product_uom_id': cls.env.ref('uom.product_uom_unit').id,
            'bom_id': cls.env.ref('mrp.mrp_bom_manufacture').id,
        }, {
            'product_id': cls.env.ref('product.product_product_27').id,
            'product_qty': 1,
            'product_uom_id': cls.env.ref('uom.product_uom_unit').id,
            'bom_id': cls.env.ref('mrp.mrp_bom_manufacture').id,
        }, {
            'product_id': cls.env.ref('mrp.product_product_wood_panel').id,
            'product_qty': 1,
            'product_uom_id': cls.env.ref('uom.product_uom_unit').id,
            'bom_id': cls.env.ref('mrp.mrp_bom_manufacture').id,
        }])

        # Test the case of product with different Purchase UoM
        cls.product_purchase_uom = cls.env.ref(
            'mrp.product_product_computer_desk_bolt_product_template'
        )
        cls.product_purchase_uom.uom_po_id = cls.env.ref('uom.product_uom_dozen')

    def test_purchase_add_products_from_bom(self):
        """ Test Purchase Add Products From BoM."""

        purchase = self.purchase_order.create({
            'partner_id': self.env.ref('base.res_partner_3').id,
        })
        wizard_obj = self.add_product_from_bom_wizard.with_context(
            default_purchase_id=purchase.id,
        )
        fields_list = wizard_obj.fields_get().keys()
        wizard_values = wizard_obj.default_get(fields_list)
        product = self.env.ref('product.product_product_3')
        # Get the first BoM
        bom = product.product_tmpl_id.bom_ids[0]
        wizard_values.update({
            'product_id': product.id,
            'bom_id': bom.id,
            'product_qty': 2,
        })
        wizard = wizard_obj.create(wizard_values)
        wizard._onchange_product_id()
        # Onchange product clean other fields
        wizard_values.update({
            'product_id': product.id,
            'bom_id': bom.id,
            'product_qty': 2,
        })
        wizard = wizard_obj.create(wizard_values)
        wizard.button_get_products_from_bom()

        # Test Explode Products with BoM
        for line in wizard.raw_product_line_ids:
            if line.bom_id:
                line.add_products_from_bom()

        # Test Return products exploded
        for line in wizard.raw_product_line_ids:
            if line.exploded_product:
                line.return_finished_products_from_bom()
                break

        # Select Products to Add in Purchase Line,
        raw_lines_qty = len(bom.bom_line_ids)
        count = 1
        for line in wizard.raw_product_line_ids:
            line._onchange_product_qty()
            line._onchange_price_unit()
            # TODO: Method compute of Field are not being call in the tests
            #  without the line below, is there anyway to work?
            line._compute_has_bom()
            # test not select all products in BoM
            if count == len(wizard.raw_product_line_ids):
                break
            count += 1

        wizard.add_products()
        # test the qty of lines add from BoM
        self.assertEqual(len(purchase.order_line), (raw_lines_qty - 1))

        # Test add same Products already exist in Purchase Line,
        # in this case it should only sum the Product Qty not duplicate line
        wizard_2 = wizard_obj.create(wizard_values)
        wizard_2.button_get_products_from_bom()

        wizard_2.add_products()

        # Check if the Product Qty keep the same
        self.assertEqual(len(purchase.order_line), raw_lines_qty)
