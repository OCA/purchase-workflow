# -*- coding: utf-8 -*-
# Author: Leonardo Pistone
# Copyright 2014 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api
from openerp.tools.translate import _


class Rule(models.Model):
    _inherit = 'procurement.rule'

    @api.model
    def _get_action(self):
        return [('buy_vci', _('Buy VCI'))] + super(Rule, self)._get_action()
