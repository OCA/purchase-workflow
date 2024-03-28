# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    def update_from_purchase_skip(self):
        return self.update_from_purchase(create=False)

    def update_from_purchase(self, create=True):
        if self:
            if create:
                vals = self._get_tmp_supplierinfo_vals()
                self.with_context(create_temporary_supplier_info=False).create(vals)
            self.env["purchase.order.line"].browse(
                self._context.get("update_from_po_line_id")
            ).supplierinfo_ok = True
        po_id = self._context.get("update_from_po_id")
        if po_id:
            # The update have been launch globally
            # so we have to return the next action
            purchase = self.env["purchase.order"].browse(po_id)
            lines = purchase.order_line.filtered(lambda s: not s.supplierinfo_ok)
            if lines:
                return lines[0].action_create_missing_supplierinfo()
        return {}  # return empty action to close the pop-up

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get("create_temporary_supplier_info"):
            assert len(vals_list) == 1
            # /!\ hack zone
            # With odoo you can not call a method before doing a save
            # in our case we do not want to save before calling
            # update_from_purchase or update_from_purchase_skip
            # so we create a temporary object where the vals will be store
            # and we return a "fake" negative ID
            # A negative is a "valid" id for the websclient but it's never used
            # in odoo so we know that it's not a real id.
            # In a long term we should implement a specific kind of action
            # in odoo frontend to be able to call a method without saving
            record = self.env["temporary.supplierinfo"]._store_vals(vals_list[0])
            return self.browse(-record.id)
        return super().create(vals_list)

    def _get_tmp_supplierinfo_vals(self):
        self.ensure_one()
        return self.env["temporary.supplierinfo"].browse(-self.id)._get_vals()

    def read(self, fields=None, load="_classic_read"):
        if self and self[0].id < 0:
            # hack to process the negative ID
            vals = self._get_tmp_supplierinfo_vals()
            data = (
                self.env["product.supplierinfo"]
                .new(vals)
                ._read_format(fnames=fields)[0]
            )
            data["id"] = self.id
            return [data]
        return super().read(fields=fields, load=load)
