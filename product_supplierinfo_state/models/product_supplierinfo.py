# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openerp import api, fields, models

_STATES = [('open', 'Open'),
           ('closed', 'Closed / Expired')]


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    state = fields.Selection(_STATES, string='State',
                             compute='_compute_state',
                             search='_search_state')

    @api.multi
    def _compute_state(self):
        today_date = fields.Date.from_string(fields.Date.today())
        for rec in self:
            rec.state = 'open'
            if rec.date_end:
                date_end = fields.Date.from_string(rec.date_end)
                if date_end < today_date:
                    rec.state = 'closed'

    def _search_state(self, operator, value):
        """Search on the state field by evaluating on all records"""
        all_records = self.search([])

        if operator == '=':
            found_ids = [a.id for a in all_records if a.state == value]
        elif operator == 'in' and isinstance(value, list):
            found_ids = [a.id for a in all_records if a.state in value]
        elif operator in ("!=", "<>"):
            found_ids = [a.id for a in all_records if a.state != value]
        elif operator == 'not in' and isinstance(value, list):
            found_ids = [a.id for a in all_records if a.state not in value]
        else:
            raise NotImplementedError(
                'Search operator %s not implemented for value %s'
                % (operator, value)
            )
        return [('id', 'in', found_ids)]
