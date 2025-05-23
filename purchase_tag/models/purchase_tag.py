# Copyright 2022 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from random import randint

from odoo import api, fields, models


class PurchaseTag(models.Model):
    _name = "purchase.tag"
    _description = "Purchase Tag"
    _parent_store = True

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Tag Name", required=True, translate=True)
    color = fields.Integer(default=lambda self: self._get_default_color())
    parent_id = fields.Many2one("purchase.tag", index=True, ondelete="cascade")
    child_ids = fields.One2many("purchase.tag", "parent_id")
    parent_path = fields.Char(index=True)

    _sql_constraints = [
        ("tag_name_uniq", "unique (name)", "Tag name already exists !"),
    ]

    def _compute_display_name(self):
        for tag in self:
            names = []
            current = tag
            while current:
                if current.name:
                    names.append(current.name)
                current = current.parent_id
            display_name = " / ".join(reversed(names))
            tag.display_name = display_name

    @api.model
    def _search_display_name(self, operator, value):
        domain = [("name", operator, value.split(" / ")[-1])]
        return domain
