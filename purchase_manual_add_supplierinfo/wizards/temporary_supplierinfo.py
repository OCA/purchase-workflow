# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import fields, models


class TemporarySupplierinfo(models.Model):
    _name = "temporary.supplierinfo"
    _description = "Temporary Supplierinfo"

    data = fields.Text()

    def _store_vals(self, vals):
        return self.create({"data": json.dumps(vals)})

    def _get_vals(self):
        return json.loads(self.data)
