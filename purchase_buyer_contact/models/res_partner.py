# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Column Section
    buyer_partner_id = fields.Many2one(
        'res.partner',
        default=lambda self: self.env.user.company_id.buyer_partner_id)
    buyer_name = fields.Char(
        related='buyer_partner_id.name', store=True, readonly="1")
    buyer_email = fields.Char(
        related='buyer_partner_id.email', store=True, readonly="1")
    buyer_phone = fields.Char(
        related='buyer_partner_id.phone', store=True, readonly="1")
    customer_code = fields.Char(
        "Customer Code", help="The code by which the supplier knows you")
