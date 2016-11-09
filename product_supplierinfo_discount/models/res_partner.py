# -*- coding: utf-8 -*-
# © 2016 GRAP (http://www.grap.coop)
#        Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields
import openerp.addons.decimal_precision as dp


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_supplierinfo_discount = fields.Float(
        string='Default Supplier Discount (%)',
        digits_compute=dp.get_precision('Discount'),
        help="This value will be used as the default one, for each new"
        " supplierinfo line depending on that supplier.")
