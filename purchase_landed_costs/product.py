#  -*- coding: utf-8 -*-
from osv import orm, fields
#----------------------------------------------------------
# Product INHERIT
#----------------------------------------------------------


class product_template(orm.Model):
    _inherit = "product.template"

    _columns = {
        'landed_cost_type': fields.selection(
            [('value', 'Value'), ('per_unit', 'Quantity'), ('none', 'None')],
            'Distribution Type',
            help="Used if this product is landed costs: If landed costs are \
            defined for purchase orders or pickings, this indicates how the \
            costs are distributed to the lines"),
        'landed_cost': fields.boolean('Calculate Landed Costs',
            help="Check this if you want to use landed cost calculation for \
            average price for this product")
    }

product_template()


class product_category(orm.Model):

    _inherit = 'product.category'
    _columns = {
        'landed_cost': fields.boolean('Calculate Landed Costs',
            help="Check this if you want to use landed cost calculation for \
            average price for this category")
    }

product_category()
