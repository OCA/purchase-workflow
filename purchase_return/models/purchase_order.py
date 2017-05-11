# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Eficent Business and IT Consulting Services
#           <contact@eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    type = fields.Selection([('purchase', 'Purchase Order'),
                             ('return', 'Return PO')],
                            readonly=True, index=True, change_default=True,
                            default=lambda self: self.env.context.
                            get('type', 'purchase'), track_visibility='always')

    @api.multi
    def action_view_invoice_refund(self):
        '''
        This function returns an action that display existing vendor refund
        bills of given purchase order id.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        refunds = self.invoice_ids.filtered(lambda x: x.type == 'in_refund')
        # override the context to get rid of the default filtering
        result['context'] = {'type': 'in_refund',
                             'default_purchase_id': self.id}

        if not refunds:
            # Choose a default account journal in the
            # same currency in case a new invoice is created
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(
                journal_domain, limit=1)
            if default_journal_id:
                result['context']['default_journal_id'] = default_journal_id.id
        else:
            # Use the same account journal than a previous invoice
            result['context']['default_journal_id'] = refunds[0].journal_id.id

        # choose the view_mode accordingly
        if len(refunds) != 1:
            result['domain'] = "[('id', 'in', " + \
                               str(refunds.ids) + ")]"
        elif len(refunds) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = refunds.id
        return result

    @api.depends('order_line.invoice_lines.invoice_id.state')
    def _compute_invoice_refund(self):
        for order in self:
            invoices = self.env['account.invoice']
            for line in order.order_line:
                invoices |= line.invoice_lines.mapped('invoice_id').filtered(
                    lambda x: x.type == 'in_refund')
            order.invoice_refund_count = len(invoices)

    @api.model
    def _default_picking_type(self):
        res = super(PurchaseOrder, self)._default_picking_type()
        if self.env.context.get('type', False) == 'return':
            type_obj = self.env['stock.picking.type']
            company_id = self.env.context.get('company_id') or \
                self.env.user.company_id.id
            types = type_obj.search([('code', '=', 'outgoing'),
                                     ('warehouse_id.company_id', '=',
                                      company_id)])
            if not types:
                types = type_obj.search([('code', '=', 'outgoing'),
                                         ('warehouse_id', '=', False)])
            res = types[:1]
        return res

    invoice_refund_count = fields.Integer(compute="_compute_invoice_refund",
                                          string='# of Invoice Refunds',
                                          copy=False, default=0)

    picking_type_id = fields.Many2one(default=_default_picking_type)

    @api.multi
    def _get_destination_location(self):
        res = super(PurchaseOrder, self)._get_destination_location()
        if self.type == 'return':
            if not self.dest_address_id:
                return self.picking_type_id.default_location_src_id.id
        return res

    @api.multi
    def _get_src_location_returns(self):
        self.ensure_one()
        if self.type == 'return':
            if self.dest_address_id:
                return self.dest_address_id.property_stock_customer.id
            return self.picking_type_id.default_location_src_id.id

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.type == 'return':
            location_id = res['location_id']
            res['location_id'] = self._get_src_location_returns()
            res['location_dest_id'] = location_id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _create_stock_moves(self, picking):
        moves = super(PurchaseOrderLine, self)._create_stock_moves(picking)
        for move in moves:
            location_id = self.env['stock.location'].browse(
                move.purchase_line_id.order_id._get_src_location_returns())
            location_dest_id = move.location_dest_id

            move.location_id = location_dest_id
            move.location_dest_id = location_id

        return moves

    @api.depends('invoice_lines.invoice_id.state',
                 'invoice_lines.invoice_id.type')
    def _compute_qty_invoiced(self):
        super(PurchaseOrderLine, self)._compute_qty_invoiced()
        for line in self:
            if line.order_id.type == 'return':
                line.qty_invoiced *= -1
