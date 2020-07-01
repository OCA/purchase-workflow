# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_plan_ids = fields.One2many(
        comodel_name='purchase.invoice.plan',
        inverse_name='purchase_id',
        string='Inovice Plan',
        copy=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    use_invoice_plan = fields.Boolean(
        string='Use Invoice Plan',
        default=False,
        copy=False,
    )
    ip_invoice_plan = fields.Boolean(
        string='Invoice Plan In Process',
        compute='_compute_ip_invoice_plan',
        help="At least one invoice plan line pending to create invoice",
    )

    @api.multi
    def _compute_ip_invoice_plan(self):
        for rec in self:
            rec.ip_invoice_plan = rec.use_invoice_plan and \
                rec.invoice_plan_ids and \
                len(rec.invoice_plan_ids.filtered(lambda l: not l.invoiced))

    @api.constrains('state')
    def _check_invoice_plan(self):
        for rec in self:
            if rec.state != 'draft':
                if rec.invoice_plan_ids.filtered(lambda l: not l.percent):
                    raise ValidationError(
                        _('Please fill percentage for all invoice plan lines'))

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda r: r.use_invoice_plan
                         and not r.invoice_plan_ids):
            raise UserError(
                _('Use Invoice Plan selected, but no plan created'))
        return super().action_confirm()

    @api.multi
    def create_invoice_plan(self, num_installment, installment_date,
                            interval, interval_type):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        invoice_plans = []
        Decimal = self.env['decimal.precision']
        prec = Decimal.precision_get('Product Unit of Measure')
        percent = float_round(1.0 / num_installment * 100, prec)
        percent_last = 100 - (percent * (num_installment-1))
        for i in range(num_installment):
            this_installment = i+1
            if num_installment == this_installment:
                percent = percent_last
            vals = {'installment': this_installment,
                    'plan_date': installment_date,
                    'invoice_type': 'installment',
                    'percent': percent}
            invoice_plans.append((0, 0, vals))
            installment_date = self._next_date(installment_date,
                                               interval, interval_type)
        self.write({'invoice_plan_ids': invoice_plans})
        return True

    @api.multi
    def remove_invoice_plan(self):
        self.ensure_one()
        self.invoice_plan_ids.unlink()
        return True

    @api.model
    def _next_date(self, installment_date, interval, interval_type):
        installment_date = fields.Date.from_string(installment_date)
        if interval_type == 'month':
            next_date = installment_date + relativedelta(months=+interval)
        elif interval_type == 'year':
            next_date = installment_date + relativedelta(years=+interval)
        else:
            next_date = installment_date + relativedelta(days=+interval)
        next_date = fields.Date.to_string(next_date)
        return next_date

    @api.multi
    def action_invoice_create(self):
        self.ensure_one()
        pre_inv = self.env['account.invoice'].new({
            'type': 'in_invoice',
            'purchase_id': self.id,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'origin': self.name,
            'name': self.partner_ref or '',
            'comment': self.notes
        })
        pre_inv.purchase_order_change()
        inv_data = pre_inv._convert_to_write(pre_inv._cache)
        invoice = self.env['account.invoice'].create(inv_data)
        invoice.compute_taxes()
        if not invoice.invoice_line_ids:
            raise UserError(
                _("There is no invoiceable line. If a product has a"
                  "Delivered quantities invoicing policy, please make sure"
                  "that a quantity has been delivered."))
        po_payment_term_id = invoice.payment_term_id.id
        fp_invoice = invoice.fiscal_position_id
        invoice._onchange_partner_id()
        invoice.fiscal_position_id = fp_invoice
        invoice.payment_term_id = po_payment_term_id
        invoice.message_post_with_view(
            'mail.message_origin_link',
            values={'self': invoice,
                    'origin': self, },
            subtype_id=self.env.ref('mail.mt_note').id)
        invoice_plan_id = self._context.get('invoice_plan_id')
        if invoice_plan_id:
            plan = self.env['purchase.invoice.plan'].browse(invoice_plan_id)
            plan._compute_new_invoice_quantity(invoice)
            invoice.date_invoice = plan.plan_date
            plan.invoice_ids += invoice
        return invoice


class PurchaseInvoicePlan(models.Model):
    _name = 'purchase.invoice.plan'
    _description = 'Invoice Planning Detail'
    _order = 'installment'

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchases Order',
        index=True,
        readonly=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
        related='purchase_id.partner_id',
        store=True,
        index=True,
    )
    state = fields.Selection(
        [('draft', 'RFQ'),
         ('sent', 'RFQ Sent'),
         ('to approve', 'To Approve'),
         ('purchase', 'Purchase Order'),
         ('done', 'Locked'),
         ('cancel', 'Cancelled'), ],
        string='Status',
        related='purchase_id.state',
        store=True,
        index=True,
    )
    installment = fields.Integer(
        string='Installment',
    )
    plan_date = fields.Date(
        string='Plan Date',
        required=True,
    )
    invoice_type = fields.Selection(
        [('installment', 'Installment')],
        string='Type',
        required=True,
        default='installment',
    )
    percent = fields.Float(
        string='Percent',
        digits=dp.get_precision('Product Unit of Measure'),
        help="This percent will be used to calculate new quantity"
    )
    invoice_ids = fields.Many2many(
        'account.invoice',
        relation="purchase_invoice_plan_invoice_rel",
        column1='plan_id',
        column2='invoice_id',
        string='Invoices',
        readonly=True,
    )
    to_invoice = fields.Boolean(
        string='Next Invoice',
        compute='_compute_to_invoice',
        help="If this line is ready to create new invoice",
    )
    invoiced = fields.Boolean(
        string='Invoice Created',
        compute='_compute_invoiced',
        help="If this line already invoiced",
    )

    @api.multi
    def _compute_to_invoice(self):
        """ If any invoice is in draft/open/paid do not allow to create inv
            Only if previous to_invoice is False, it is eligible to_invoice
        """
        for rec in self.sorted('installment'):
            rec.to_invoice = False
            if rec.purchase_id.state != 'purchase':
                # Not confirmed, no to_invoice
                continue
            if not rec.invoiced:
                rec.to_invoice = True
                break

    @api.multi
    def _compute_invoiced(self):
        for rec in self:
            invoiced = rec.invoice_ids.filtered(
                lambda l: l.state in ('draft', 'open', 'paid'))
            rec.invoiced = invoiced and True or False

    @api.multi
    def _compute_new_invoice_quantity(self, invoice):
        self.ensure_one()
        percent = self.percent
        for line in invoice.invoice_line_ids:
            assert len(line.purchase_line_id) >= 0, \
                'No matched order line for invoice line'
            order_line = fields.first(line.purchase_line_id)
            plan_qty = self._get_plan_qty(order_line, percent)
            prec = order_line.product_uom.rounding
            if float_compare(abs(plan_qty), abs(line.quantity), prec) == 1:
                raise ValidationError(
                    _('Plan quantity: %s, exceed invoiceable quantity: %s'
                      '\nProduct should be delivered before invoice') %
                    (plan_qty, line.quantity))
            line.write({'quantity': plan_qty})
        invoice.compute_taxes()

    @api.model
    def _get_plan_qty(self, order_line, percent):
        plan_qty = order_line.product_qty * (percent/100)
        return plan_qty
