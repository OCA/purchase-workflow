# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from urllib import urlencode
from urlparse import urljoin

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ'),
        ('bid', 'Bid Received'),

        # States Added
        ('wait_valid', 'Waiting for Validation'),
        ('wait_correct', 'Waiting for Correction'),
        ('wait', 'Waiting'),
        ('validated', 'Validated'),

        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Confirmed'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ]

    state = fields.Selection(STATE_SELECTION)

    @api.multi
    def wkf_wait_validation_order(self):
        for po in self:
            if not po.order_line:
                raise ValidationError(
                    _('You can not wait for purchase order to be validated '
                      'without Purchase Order Lines.'))
            message = _(
                "Purchase order '%s' is waiting for validation."
            ) % (po.name,)
            po.message_post(body=message)

        self.write({'state': 'wait_valid'})
        return True

    @api.multi
    def wkf_wait_correction(self):
        self.write({'state': 'wait_correct'})
        return True

    @api.multi
    def wkf_validated(self):
        self.write({'state': 'validated'})
        return True

    @api.multi
    def test_require_validation(self):
        limit = (
            self.env["purchase.config.settings"].get_default_limit_amount()
            ["limit_amount"]
        )
        for rec in self:
            if rec.amount_total >= limit:
                return True

        return False

    @api.multi
    def get_validator_emails(self):
        grp = self.env.ref(
            "purchase_internal_validation.group_purchase_validator")
        emails = [
            user.email
            for user in grp.users
            if user.email
        ]
        return emails

    @api.multi
    def get_action_url(self):
        self.ensure_one()

        base_url = self.env['ir.config_parameter'].get_param(
            'web.base.url', default='http://localhost:8069')
        query = {'db': self.env.cr.dbname}
        fragment = {'id': self.id, 'model': self._name}
        return urljoin(base_url, "?%s#%s" % (
            urlencode(query), urlencode(fragment)
        ))
