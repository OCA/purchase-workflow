from random import randint

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseTag(models.Model):
    _name = "purchase.tag"
    _description = "Purchase Tag"
    _parent_store = True

    # Fields
    name = fields.Char("Tag Name", required=True, translate=True)
    color = fields.Integer(default=lambda self: self._get_default_color())
    parent_id = fields.Many2one("purchase.tag", index=True, ondelete="cascade")
    child_ids = fields.One2many("purchase.tag", "parent_id")
    parent_path = fields.Char(index=True)
    display_name = fields.Char(compute="_compute_display_name")

    _sql_constraints = [
        ("tag_name_uniq", "unique (name)", "Tag name already exists !"),
    ]

    def _get_default_color(self):
        return randint(1, 11)

    @api.depends("name", "parent_id")
    def _compute_display_name(self):
        for rec in self:
            if rec.parent_id and rec.parent_id.name:
                rec.display_name = f"{rec.parent_id.name}/{rec.name}"
            else:
                rec.display_name = rec.name

    @api.model
    def _search_display_name(self, operator, value, limit=100):
        if value:
            domain = ["|", ("name", operator, value), ("parent_path", operator, value)]
            return self.search(domain, limit=limit).ids
        return super()._search_display_name(operator=operator, value=value)

    @api.constrains("parent_id")
    def _check_parent_recursion(self):
        if self._has_cycle("parent_id"):
            raise ValidationError(self.env._("Tags cannot be recursive."))
