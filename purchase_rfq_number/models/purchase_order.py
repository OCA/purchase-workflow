# Copyright 2021 ProThai Technology Co.,Ltd. (http://prothaitechnology.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    rfq_number = fields.Char(
        string="RFQ Reference",
        index=True,
        copy=False,
        default="New",
    )

    @api.model
    def create(self, vals):

        if "company_id" in vals:
            keep_name_po = (
                self.env["res.company"].browse(vals.get("company_id")).keep_name_po
            )
        else:
            keep_name_po = self.env.company.keep_name_po

        if not keep_name_po and vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("purchase.rfq") or "New"

        return super().create(vals)

    def button_confirm(self):
        for order in self:
            if order.state in ["draft", "sent"] and not order.company_id.keep_name_po:
                if order.company_id.auto_attachment_rfq:
                    # save rfq pdf as attachment
                    order.action_get_rfq_attachment()

                order.write(
                    {
                        "rfq_number": order.name,
                        "name": self.env["ir.sequence"].next_by_code("purchase.order"),
                    }
                )

        return super().button_confirm()

    def action_get_rfq_attachment(self):
        rfq_pdf = self.env.ref("purchase.report_purchase_quotation")._render_qweb_pdf(
            self.id
        )[0]
        return self.env["ir.attachment"].create(
            {
                "name": "{}.pdf".format(self.name),
                "type": "binary",
                "datas": base64.encodebytes(rfq_pdf),
                "res_model": self._name,
                "res_id": self.id,
            }
        )

    def button_draft(self):
        for rec in self.filtered(lambda l: l.rfq_number != "New"):
            rec.name = rec.rfq_number
        return super().button_draft()
