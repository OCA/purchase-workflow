#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_valid_psi = fields.Selection(
        [
            ('first', 'Consider only the first supplier on the product'),
            ('all', 'Consider all the suppliers registered on the product'),
        ], 'Supplier choice', default='first',
        default_model='computed.purchase.order',
        config_parameter='purchase_compute_order.default_valid_psi'
    )
