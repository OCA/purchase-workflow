# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, exceptions, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _purchase_request_confirm_message_content(self, request,
                                                  request_dict):
        self.ensure_one()
        if not request_dict:
            request_dict = {}
        title = _('Order confirmation %s for your Request %s') % (
            self.name, request.name)
        message = '<h3>%s</h3><ul>' % title
        message += _('The following requested items from Purchase Request %s '
                     'have now been confirmed in Purchase Order %s:') % (
            request.name, self.name)

        for line in request_dict.values():
            message += _(
                '<li><b>%s</b>: Ordered quantity %s %s, Planned date %s</li>'
            ) % (line['name'],
                 line['product_qty'],
                 line['product_uom'],
                 line['date_planned'],
                 )
        message += '</ul>'
        return message

    @api.multi
    def _purchase_request_confirm_message(self):
        request_obj = self.env['purchase.request']
        for po in self:
            requests_dict = {}
            for line in po.order_line:
                for request_line in line.sudo().purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    date_planned = "%s" % line.date_planned
                    data = {
                        'name': request_line.name,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.name,
                        'date_planned': date_planned,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict:
                request = request_obj.sudo().browse(request_id)
                message = po._purchase_request_confirm_message_content(
                    request, requests_dict[request_id])
                request.message_post(body=message, subtype='mail.mt_comment')
        return True

    @api.multi
    def _purchase_request_line_check(self):
        for po in self:
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    if request_line.sudo().purchase_state == 'done':
                        raise exceptions.UserError(
                            _('Purchase Request %s has already '
                              'been completed') % request_line.request_id.name)
        return True

    @api.multi
    def button_confirm(self):
        self._purchase_request_line_check()
        res = super(PurchaseOrder, self).button_confirm()
        self._purchase_request_confirm_message()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_request_lines = fields.Many2many(
        'purchase.request.line',
        'purchase_request_purchase_order_line_rel',
        'purchase_order_line_id',
        'purchase_request_line_id',
        'Purchase Request Lines', readonly=True, copy=False)

    @api.multi
    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids += line.purchase_request_lines.ids

        domain = [('id', 'in', request_line_ids)]

        return {'name': _('Purchase Request Lines'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request.line',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': domain}
