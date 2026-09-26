from odoo import fields, models


class ContainerType(models.Model):
    _name = "container.type"
    _description = "Usual containers"

    name = fields.Char()
    description = fields.Char()
