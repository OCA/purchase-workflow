# Copyright 2021 Akretion - www.akretion.com.br -
# @author  Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AddProductsFromBoM(models.TransientModel):
    _name = "add.products.from.bom"
    _description = "Purchase Add Products From BoM"

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
    )
    bom_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='Bill of Material',
    )
    # Used to create Domain
    bom_ids = fields.One2many(
        comodel_name='mrp.bom',
        related='product_id.product_tmpl_id.bom_ids',
        string='Bill of Materials'
    )
    product_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
        default=1,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )
    raw_product_line_ids = fields.One2many(
        comodel_name='add.products.from.bom.lines',
        inverse_name='product_finished_id',
        string='Raw Products'
    )

    def button_get_products_from_bom(self):

        if self.product_id and self.product_qty and self.bom_id:
            material_list = self.get_products_from_bom(
                self.product_id, self.product_qty, self.bom_id
            )
            self.raw_product_line_ids = [(5,)] + [(0, 0, x) for x in material_list]

        # Avoid close wizard after click the button 'Get Products from BoM'
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.products.from.bom',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def get_products_from_bom(self, finished_product, product_qty, bom_id):

        product_uom_id = \
            finished_product.uom_po_id or finished_product.uom_id
        material_list = []

        factor = product_uom_id._compute_quantity(
            product_qty,
            bom_id.product_uom_id) / bom_id.product_qty

        boms, lines = bom_id.explode(
            finished_product, factor, picking_type=bom_id.picking_type_id)

        for line in lines:
            product = line[0].product_id
            product_qty = line[1].get('qty')
            product_uom = line[0].product_uom_id
            purchase_uom = product.uom_po_id

            # Check if product has other UOM for Purchase
            if product_uom != purchase_uom:
                # Convert Qty
                product_qty = line[0].product_uom_id._compute_quantity(
                    product_qty, purchase_uom
                )

            # Get Price Unit to show in wizard and allow to user see and
            # change if they wanted before include in purchase line.
            values = self._simulate_purchase_line_onchanges(
                product, product_qty, product_uom,
            )
            price_unit = values.get('price_unit')

            # If not vendors price use the Cost Price
            if not price_unit:
                price_unit = product.standard_price

            bom = False
            if len(product.product_tmpl_id.bom_ids) == 1:
                bom = product.product_tmpl_id.bom_ids.id

            values = {
                'product_id': product.id,
                'orig_bom_product_id': finished_product.id,
                'bom_id': bom,
                'product_qty': product_qty,
                'product_uom_id': product_uom.id,
                'purchase_uom_id': purchase_uom.id,
                'price_unit': price_unit,
            }

            material_list.append(values)

        return material_list

    @api.onchange('product_id')
    def _onchange_product_id(self):
        # Clean fields.
        # Check if the wizard not been call from purchase line,
        # case Product has another Product with BoM inside the
        # product_qty should be pass in context
        if not self.env.context.get('default_product_qty'):
            self.bom_id = False
            self.product_uom_id = False
            self.list_prod_already_exp = False
            self.raw_product_line_ids = [(5, 0, 0)]

        # Case one BoM, filled field.
        if self.product_id.bom_count == 1:
            self.bom_id = self.product_id.bom_ids[0]

    def _simulate_purchase_line_onchanges(self, product, product_qty, product_uom):
        """
        Simulate onchanges for purchase line
        :param values: dict
        :return: dict
        """
        purchase_line_obj = self.env['purchase.order.line']

        values = purchase_line_obj.default_get(
            purchase_line_obj.fields_get().keys()
        )

        values.update({
            'product_id': product,
            'product_qty': product_qty,
            'product_uom': product_uom,
        })

        purchase_line = self.env['purchase.order.line'].new(values.copy())
        purchase_line.onchange_product_id()

        # After onchange product_qty are change for 1
        purchase_line.product_qty = values.get('product_qty')

        purchase_line._onchange_quantity()
        new_values = purchase_line._convert_to_write(purchase_line._cache)
        # Ensure basic values are not updated
        values.update(new_values)

        return values

    def add_products(self):
        for line in self.raw_product_line_ids:

            # Only Select Products should be add
            if not line.selected_product:
                continue

            # If product already in line just sum to
            # product_qty to avoid duplicate lines.
            product_already_in_line = self.purchase_id.order_line.search([
                ('order_id', '=', self.purchase_id.id),
                ('product_id', '=', line.product_id.id),
            ])

            if product_already_in_line:
                product_already_in_line.product_qty += line.product_qty
            else:
                values = self._get_values_purchase_line(line)
                self.purchase_id.order_line.create(values)

    def _get_values_purchase_line(self, line):
        values = self._simulate_purchase_line_onchanges(
            line.product_id,
            line.product_qty,
            line.product_uom_id,
        )
        values['order_id'] = self.purchase_id.id
        # Price informed by user has priority
        values['price_unit'] = line.price_unit
        return values


class AddProductsFromBoMLines(models.TransientModel):
    _name = "add.products.from.bom.lines"
    _description = "Purchase Add Products From BoM Line"

    # Use in view to show or not Button to explode semi finished products
    has_bom = fields.Boolean(compute='_compute_has_bom')

    product_finished_id = fields.Many2one(
        comodel_name='add.products.from.bom'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product'
    )
    orig_bom_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Origin BoM Product',
        readonly=True,
    )
    bom_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='Bill of Material',

    )
    # Used to create Domain
    bom_ids = fields.One2many(
        comodel_name='mrp.bom',
        related='product_id.product_tmpl_id.bom_ids',
        string='Bill of Materials'
    )
    product_qty = fields.Float(
        string='Quantity to Buy',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure'
    )
    purchase_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Purchase Unit of Measure'
    )
    # fields.Monetary required Currency field to avoid error:
    #  AssertionError: Field purchase.add.products.from.bom.line.price_unit
    #  with unknown currency_field None
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='product_finished_id.currency_id',
    )
    price_unit = fields.Monetary(
        string='Unit Price',
        currency_field='currency_id',
    )
    product_qty_stock = fields.Float(
        string='Quantity Available in Stock',
        related='product_id.qty_available'
    )
    product_qty_after_buy = fields.Float(
        string='Quantity After Buy',
        compute='_compute_product_qty_after_buy',
    )
    total_product_value = fields.Monetary(
        string='Total Product Value',
        currency_field='currency_id',
        compute='_compute_total_product_value',
    )
    selected_product = fields.Boolean(
        string='Selected Product',
        default=True,
    )
    exploded_product = fields.Boolean(string='Already Exploded Product')

    # Use for Return Products from BoM
    main_bom_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Main BoM Product',
        readonly=True,
    )

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        self._compute_product_qty_after_buy()

    def _compute_product_qty_after_buy(self):
        for record in self:
            product_qty = record.product_qty
            # Show stock qty in Product UoM
            if record.purchase_uom_id != record.product_uom_id:
                product_qty = record.purchase_uom_id._compute_quantity(
                    record.product_qty,
                    record.product_uom_id
                )

            record.product_qty_after_buy = \
                record.product_qty_stock + product_qty

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        self._compute_total_product_value()

    def _compute_total_product_value(self):
        for record in self:
            record.total_product_value = \
                record.price_unit * record.product_qty

    def _compute_has_bom(self):
        for line in self:
            has_bom = any(line.product_id.product_tmpl_id.bom_ids)
            if line.exploded_product:
                has_bom = False
            line.has_bom = has_bom

    def add_products_from_bom(self):
        # In the case of Finished Product has another Product with BoM inside
        # the type Kit/phanton will be explode the type Manufacture this
        # product/normal will appear with button Add Products From BoM to
        # make it possible, the case the product has more than one BoM
        # wizard will appear to user can choose.
        self.ensure_one()
        if not self.bom_id:
            raise UserError(_("Select one of the BoMs."))

        material_list = \
            self.product_finished_id.get_products_from_bom(
                self.product_id, self.product_qty, self.bom_id
            )

        self.exploded_product = True
        # Explode product should be not Selected
        self.selected_product = False
        for values in material_list:
            values['product_finished_id'] = self.product_finished_id.id
            # The way found to be able unexploded products
            # with has other BoMs inside
            if values['orig_bom_product_id'] != self.orig_bom_product_id.id:
                if self.main_bom_product_id:
                    values['main_bom_product_id'] = self.main_bom_product_id.id
                else:
                    values['main_bom_product_id'] = self.product_id.id

            else:
                values['main_bom_product_id'] = self.product_id.id

            self.create(values)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.products.from.bom',
            'res_id': self.product_finished_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    def return_finished_products_from_bom(self):
        products_to_delete = self.product_finished_id.raw_product_line_ids.search([
            ('main_bom_product_id', '=', self.product_id.id),
            ('product_finished_id', '=', self.product_finished_id.id)
        ])

        products_to_delete.unlink()
        self.exploded_product = False
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.products.from.bom',
            'res_id': self.product_finished_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
