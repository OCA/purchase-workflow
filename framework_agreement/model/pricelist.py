# -*- coding: utf-8 -*-
#    Author: Nicolas Bessi, Leonardo Pistone
#    Copyright 2013-2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import time
from openerp import models, fields, api, tools, exceptions, osv


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    portfolio_id = fields.Many2one(
        'framework.agreement.portfolio',
        'Portfolio',
    )

    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver to')
    payment_term_id = fields.Many2one('account.payment.term', 'Payment terms')
    terms_of_payment = fields.Char()
    incoterm_id = fields.Many2one(
        'stock.incoterms',
        'Incoterm',
        help="International Commercial Terms are a series of predefined "
        "commercial terms used in international transactions.")
    origin_address_id = fields.Many2one('res.partner', 'Origin Address')
    dest_address_id = fields.Many2one('res.partner', 
                                      'Customer Address (Direct Delivery)')
    origin_address_id = fields.Many2one('res.partner', 'Origin Address')
    incoterm_address = fields.Char('Incoterm Address')
    shipment_origin_id = fields.Many2one('res.partner', 'Shipment Origin')
    supplierinfo_ids = fields.One2many('product.supplierinfo',
                                       'agreement_pricelist_id')

    def _price_rule_get_multi(self, cr, uid, pricelist,
                              products_by_qty_by_partner, context=None):
        context = context or {}
        date = context.get('date') or time.strftime('%Y-%m-%d')

        products = map(lambda x: x[0], products_by_qty_by_partner)
        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.template')
        product_uom_obj = self.pool.get('product.uom')
        price_type_obj = self.pool.get('product.price.type')

        if not products:
            return {}

        version = False
        for v in pricelist.version_id:
            if (
                (v.date_start is False) or
                (v.date_start <= date)) and (
                    (v.date_end is False) or
                    (v.date_end >= date)
                    ):
                version = v
                break
        if not version:
            raise osv.except_osv(
                _('Warning!'),
                _("At least one pricelist has no active version !\n"
                  "Please create or activate one."))
        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            prod_ids = [product.id for product in tmpl.product_variant_ids
                        for tmpl in products]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id
                             for product in products]

        # Load all rules
        cr.execute(
            'SELECT i.id '
            'FROM product_pricelist_item AS i '
            'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = any(%s)) '
            'AND (product_id IS NULL OR (product_id = any(%s))) '
            'AND ((categ_id IS NULL) OR (categ_id = any(%s))) '
            'AND (price_version_id = %s) '
            'ORDER BY sequence, min_quantity desc',
            (prod_tmpl_ids, prod_ids, categ_ids, version.id))

        item_ids = [x[0] for x in cr.fetchall()]
        items = self.pool.get('product.pricelist.item').browse(
            cr, uid, item_ids, context=context)

        price_types = {}

        results = {}
        for product, qty, partner in products_by_qty_by_partner:
            results[product.id] = 0.0
            rule_id = False
            price = False

            # Final unit price is computed according to `qty` in the
            # `qty_uom_id` UoM.  An intermediary unit price may be computed
            # according to a different UoM, in which case the price_uom_id
            # contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = product_uom_obj._compute_qty(
                        cr, uid, context['uom'], qty, product.uom_id.id or
                        product.uos_id.id)
                except exceptions.except_orm:
                    # Ignored - incompatible UoM in context, use default
                    #  product UoM
                    pass

            for rule in items:

                if (rule.min_quantity and
                        qty_in_product_uom < rule.min_quantity):
                    continue
                if is_product_template:
                    if (
                        rule.product_tmpl_id and
                        product.id != rule.product_tmpl_id.id
                    ):
                        continue
                    if rule.product_id:
                        continue
                else:
                    if (
                        rule.product_tmpl_id and
                        product.product_tmpl_id.id != rule.product_tmpl_id.id
                    ):
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == -1:
                    if rule.base_pricelist_id:
                        price_tmp = self._price_get_multi(
                            cr, uid,
                            rule.base_pricelist_id,
                            [(product, qty, partner)],
                            context=context)[product.id]
                        ptype_src = rule.base_pricelist_id.currency_id.id
                        price_uom_id = qty_uom_id
                        price = currency_obj.compute(
                            cr, uid,
                            ptype_src, pricelist.currency_id.id,
                            price_tmp, round=False,
                            context=context)
                elif rule.base == -2:
                    seller = False
                    for seller_id in product.seller_ids:
                        # framework_agreement START
                        if rule.use_agreement_prices:
                            if (
                                seller_id.agreement_pricelist_id !=
                                rule.price_version_id.pricelist_id
                            ):
                                continue
                        # framework_agreement END
                        if (not partner) or (seller_id.name.id != partner):
                            continue
                        seller = seller_id
                    if not seller and product.seller_ids:
                        # framework_agreement START
                        if not rule.use_agreement_prices:
                            seller = product.seller_ids[0]
                        # framework_agreement END
                    if seller:
                        qty_in_seller_uom = qty
                        seller_uom = seller.product_uom.id
                        if qty_uom_id != seller_uom:
                            qty_in_seller_uom = product_uom_obj._compute_qty(
                                cr, uid, qty_uom_id, qty, to_uom_id=seller_uom)
                        price_uom_id = seller_uom
                        for line in seller.pricelist_ids:
                            if line.min_quantity <= qty_in_seller_uom:
                                price = line.price

                else:
                    if rule.base not in price_types:
                        price_types[rule.base] = price_type_obj.browse(
                            cr, uid, int(rule.base))
                    price_type = price_types[rule.base]

                    # price_get returns the price in the context UoM, i.e.
                    # qty_uom_id
                    price_uom_id = qty_uom_id
                    price = currency_obj.compute(
                        cr, uid,
                        price_type.currency_id.id,
                        pricelist.currency_id.id,
                        product_obj._price_get(
                            cr, uid, [product],
                            price_type.field,
                            context=context)[product.id],
                        round=False, context=context)

                if price is not False:
                    price_limit = price
                    price = price * (1.0+(rule.price_discount or 0.0))
                    if rule.price_round:
                        price = tools.float_round(
                            price,
                            precision_rounding=rule.price_round)

                    convert_to_price_uom = (
                        lambda price: product_uom_obj._compute_price(
                            cr, uid, product.uom_id.id,
                            price, price_uom_id))
                    if rule.price_surcharge:
                        price_surcharge = convert_to_price_uom(
                            rule.price_surcharge)
                        price += price_surcharge

                    if rule.price_min_margin:
                        price_min_margin = convert_to_price_uom(
                            rule.price_min_margin)
                        price = max(price, price_limit + price_min_margin)

                    if rule.price_max_margin:
                        price_max_margin = convert_to_price_uom(
                            rule.price_max_margin)
                        price = min(price, price_limit + price_max_margin)

                    rule_id = rule.id
                break

            # Final price conversion to target UoM
            price = product_uom_obj._compute_price(cr, uid, price_uom_id,
                                                   price, qty_uom_id)

            results[product.id] = (price, rule_id)
        return results

    @api.model
    def XXX_price_rule_get_multi(self, pricelist, products_by_qty_by_partner):
        """attempt to avoid repeating 200 lines"""
        Rule = self.env['product.pricelist.item']
        Product = self.env['product.product']
        SupplierInfo = self.env['product.supplierinfo']

        result = super(Pricelist, self)._price_rule_get_multi(
            pricelist, products_by_qty_by_partner)

        for product_id, (price, rule_id) in result.iteritems():
            rule = Rule.browse(rule_id)
            if rule.use_agreement_prices:
                product = Product.browse(product_id)
                supinfo = SupplierInfo.search([
                    ('product_tmpl_id', '=', product.product_template_id),
                    ('agreement_id', '=', rule.version_id.pricelist_id),
                ])
                if supinfo:
                    for priceinfo in supinfo[0].pricelist_ids:
                        pass  # XXX
                else:
                    result[product_id] = (False, False)

        return result


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    use_agreement_prices = fields.Boolean()


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    agreement_pricelist_id = fields.Many2one('product.pricelist',
                                             'Agreement pricelist')
