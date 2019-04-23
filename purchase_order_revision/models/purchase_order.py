# Copyright 2019 Akretion - Renato Lima (<http://akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('current_revision_id', 'old_revision_ids')
    def _has_old_revisions(self):
        for order in self:
            if order.old_revision_ids:
                order.has_old_revisions = True

    current_revision_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Current revision',
        readonly=True,
        copy=True)

    old_revision_ids = fields.One2many(
        comodel_name='purchase.order',
        inverse_name='current_revision_id',
        string='Old revisions',
        readonly=True,
        context={'active_test': False})

    revision_number = fields.Integer(
        string='Revision',
        copy=False,
        default=0)

    unrevisioned_name = fields.Char(
        string='Unrevisioned Order Ref',
        copy=True,
        readonly=True)

    active = fields.Boolean(
        string='Active',
        default=True)

    has_old_revisions = fields.Boolean(
        string='Has old revisions',
        compute='_has_old_revisions')

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Order Reference and revision must be unique per Company.'),
    ]

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if default.get('name', 'New') == 'New':
            seq = self.env['ir.sequence']
            default['name'] = seq.next_by_code('purchase.order') or 'New'
            default['revision_number'] = 0
            default['unrevisioned_name'] = default['name']
        return super(PurchaseOrder, self).copy(default=default)

    def copy_revision_with_context(self):
        default_data = self.default_get([])
        new_rev_number = self.revision_number + 1
        default_data .update({
            'revision_number': new_rev_number,
            'unrevisioned_name': self.unrevisioned_name,
            'name': '%s-%02d' % (self.unrevisioned_name, new_rev_number),
            'old_revision_ids': [(4, self.id, False)],
        })
        new_revision = self.copy(default_data)
        self.old_revision_ids.write({
            'current_revision_id': new_revision.id})
        self.write({'active': False,
                    'state': 'cancel',
                    'current_revision_id': new_revision.id})

        return new_revision

    @api.model
    def create(self, values):
        if 'unrevisioned_name' not in values:
            if values.get('name', 'New') == 'New':
                seq = self.env['ir.sequence']
                values['name'] = seq.next_by_code('purchase.order') or 'New'
            values['unrevisioned_name'] = values['name']
        return super(PurchaseOrder, self).create(values)

    @api.multi
    def create_revision(self):
        revision_ids = []
        # Looping over purchase order records
        for order_rec in self:
            # Calling  Copy method
            copied_rec = order_rec.copy_revision_with_context()

            msg = _('New revision created: %s') % copied_rec.name
            copied_rec.message_post(body=msg)
            order_rec.message_post(body=msg)

            revision_ids.append(copied_rec.id)

        action = {
            'type': 'ir.actions.act_window',
            'name': _('New Purchase Order Revisions'),
            'res_model': 'purchase.order',
            'domain': "[('id', 'in', %s)]" % revision_ids,
            'auto_search': True,
            'views': [
                (self.env.ref('purchase.purchase_order_tree').id, 'tree'),
                (self.env.ref('purchase.purchase_order_form').id, 'form')],
            'target': 'current',
            'nodestroy': True,
        }

        # Returning the new purchase order view with new record.
        return action
