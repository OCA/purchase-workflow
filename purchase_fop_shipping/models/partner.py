# © 2014-2016 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fop_shipping = fields.Float(
        string="FOP shipping",
        help="Min purchase order amount for FOP shipping",
        company_dependent=True,
        digits="Account",
    )
