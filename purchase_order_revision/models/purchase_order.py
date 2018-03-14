# -*- coding: utf-8 -*-
# Copyright 2013 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2015 Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    current_revision_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Current revision',
        readonly=True,
    )
    old_revision_ids = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='current_revision_id',
        string='Old revisions',
        readonly=True,
        context={'active_test': False},
    )
    revision_number = fields.Integer(
        string='Revision',
        copy=False,
    )
    unrevisioned_name = fields.Char(
        string='Order Reference',
        copy=False,
        readonly=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]

    @api.multi
    def new_revision(self):
        self.ensure_one()
        old_name = self.name
        revno = self.revision_number
        self.write({'name': '%s-%02d' % (self.unrevisioned_name,
                                         revno + 1),
                    'revision_number': revno + 1})
        defaults = {'name': old_name,
                    'revision_number': revno,
                    'active': False,
                    'state': 'cancel',
                    'current_revision_id': self.id,
                    'unrevisioned_name': self.unrevisioned_name,
                    }
        old_revision = super(PurchaseOrder, self).copy(default=defaults)
        self.button_draft()
        msg = _('New revision created: %s') % self.name
        self.message_post(body=msg)
        old_revision.message_post(body=msg)
        return True

    @api.model
    def create(self, values):
        if 'unrevisioned_name' not in values:
            if values.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                values['name'] = seq.next_by_code('purchase.order') or '/'
            values['unrevisioned_name'] = values['name']
        return super(PurchaseOrder, self).create(values)
