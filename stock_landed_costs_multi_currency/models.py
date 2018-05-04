# -*- coding: utf-8 -*-

from openerp import models, fields, api
# TODO improve this.
ALLOWED_DIFFERENCE = 0.1


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    # using old API because the old method is implemented in old API
    def _check_sum(self, cr, uid, landed_cost, context=None):
        """
        Will check if each cost line its valuation lines sum
        to the correct amount
        and if the overall total amount is correct also

        Totally over write this method.
        """
        costcor = {}
        tot = 0
        for valuation_line in landed_cost.valuation_adjustment_lines:
            if costcor.get(valuation_line.cost_line_id):
                costcor[valuation_line.cost_line_id] += \
                    valuation_line.additional_landed_cost
            else:
                costcor[valuation_line.cost_line_id] = \
                    valuation_line.additional_landed_cost
            tot += valuation_line.additional_landed_cost
        # change begins
        # rewrite this part to allow small difference.
        # TODO to improve this part
        res = (abs(tot - landed_cost.amount_total) <= ALLOWED_DIFFERENCE)
        # change beds
        for costl in costcor.keys():
            if abs(costcor[costl] - costl.price_unit) > ALLOWED_DIFFERENCE:
                res = False
        return res


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    @api.model
    def _default_currency(self):
        '''Default currency is the company currency'''
        currency_id = self.env.user.company_id.currency_id.id
        return currency_id

    # TODO dp digit
    amount_currency = fields.Float(
        'Currency Amount')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', default=_default_currency)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            pricelist = self.partner_id.property_product_pricelist_purchase
            currency_id = pricelist.currency_id
            self.currency_id = currency_id and currency_id.id or False

    @api.onchange('amount_currency', 'currency_id')
    def onchange_amount_currency(self):
        if self.amount_currency and self.currency_id:
            # get default currency
            default_currency = self.env.user.company_id.currency_id
            assert default_currency

            if self.currency_id != default_currency:
                # new API for V 8
                self.price_unit = default_currency.compute(
                    self.amount_currency, self.currency_id)
            else:
                self.price_unit = self.amount_currency
