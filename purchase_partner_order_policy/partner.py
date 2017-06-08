# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_order_policy = fields.Selection([
        ('manual', 'Based on Purchase Order lines'),
        ('picking', 'Based on incoming shipments'),
        ('order', 'Based on generated draft invoice')
        ],
        string='Supplier Create Invoice', company_dependent=True,
        help='Select the default create invoice method for the purchase orders'
        'of this customer')

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res += ['supplier_order_policy']
        return res
