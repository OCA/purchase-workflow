# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_compare


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
                        raise exceptions.Warning(
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

    @api.multi
    def _prepare_stock_moves(self, picking):
        """Link move_dest_id when purchase request

        If the POL is linked to a purchase request, there is no
        self.procurement_ids but self.purchase_request_lines.procurement_id
        This function is mainly a copy past from product/_prepare_stock_moves
        """
        self.ensure_one()
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        if len(res) == 0:
            # super return [] if nothing to do
            return res
        qty = 0.0
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel'):
            qty += move.product_uom_qty
        diff_quantity = self.product_qty - qty
        # Fullfill all related procurements with this po line
        if self.purchase_request_lines:
            template = res.pop()
            for proc in self.purchase_request_lines.mapped(
                'procurement_id'
            ).filtered(lambda p: p.state != 'cancel'):
                # If the procurement has some moves already,
                # we should deduct their quantity
                sum_existing_moves = sum(
                    x.product_qty for x in proc.move_ids
                    if x.state != 'cancel')
                existing_proc_qty = proc.product_id.uom_id._compute_quantity(
                    sum_existing_moves, proc.product_uom)
                procurement_qty = proc.product_uom._compute_quantity(
                    proc.product_qty, self.product_uom) - existing_proc_qty
                if (
                    float_compare(
                        procurement_qty, 0.0,
                        precision_rounding=proc.product_uom.rounding
                    ) > 0 and
                    float_compare(
                        diff_quantity, 0.0,
                        precision_rounding=self.product_uom.rounding) > 0
                ):
                    tmp = template.copy()
                    tmp.update({
                        'product_uom_qty': min(procurement_qty, diff_quantity),
                        'move_dest_id': proc.move_dest_id.id,
                        # move destination is same as procurement destination
                        'procurement_id': proc.id,
                        'propagate': proc.rule_id.propagate,
                    })
                    res.append(tmp)
                    diff_quantity -= min(procurement_qty, diff_quantity)
            if float_compare(
                diff_quantity, 0.0,
                precision_rounding=self.product_uom.rounding
            ) > 0:
                template['product_uom_qty'] = diff_quantity
                res.append(template)
        return res
