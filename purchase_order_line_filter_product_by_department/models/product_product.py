from odoo import api, models


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("purchase_order"):
            if args is None:
                args = []
            args += [
                (
                    "categ_id.hr_department_id",
                    "=",
                    self.env.user.employee_id.department_id.id,
                ),
            ]

        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if self.env.context.get("purchase_order"):
            if args is None:
                args = []
            args += [
                (
                    "categ_id.hr_department_id",
                    "=",
                    self.env.user.employee_id.department_id.id,
                ),
            ]
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
