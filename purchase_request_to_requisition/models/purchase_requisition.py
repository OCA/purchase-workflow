# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, models
from odoo import _


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    @api.model
    def _purchase_request_confirm_message_content(self, pr, request,
                                                  request_dict):
        if not request_dict:
            request_dict = {}
        title = _('Bid confirmation %s for your Request %s') % (
            pr.name, request.name)
        message = '<h3>%s</h3><ul>' % title
        message += _('The following requested items from Purchase Request %s '
                     'have now being sent to Suppliers using Purchase Bid '
                     '%s:') % (
            request.name, pr.name)

        for line in request_dict.values():
            message += _(
                '<li><b>%s</b>: Total bid quantity %s %s</li>'
            ) % (line['name'],
                 line['product_qty'],
                 line['product_uom_id'],
                 )
        message += '</ul>'
        return message

    @api.multi
    def _purchase_request_confirm_message(self):
        request_obj = self.env['purchase.request']
        for pr in self:
            requests_dict = {}
            for line in pr.line_ids:
                for request_line in line.purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    data = {
                        'name': request_line.name,
                        'product_qty': line.product_qty,
                        'product_uom_id': line.product_uom_id.name,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict.keys():
                request = request_obj.browse(request_id)
                message = self._purchase_request_confirm_message_content(
                    pr, request, requests_dict[request_id])
                request.message_post(body=message, subtype='mail.mt_comment')
        return True

    @api.multi
    def action_in_progress(self):
        res = super(PurchaseRequisition, self).action_in_progress()
        self._purchase_request_confirm_message()
        return res
