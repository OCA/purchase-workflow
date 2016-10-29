# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api
from openerp.tools import float_is_zero
import logging

logger = logging.getLogger(__name__)


class PurchaseOrderImport(models.TransientModel):
    _name = 'purchase.order.import'
    _inherit = ['purchase.order.import', 'base.ubl']

    @api.model
    def parse_xml_quote(self, xml_root):
        start_tag = '{urn:oasis:names:specification:ubl:schema:xsd:'
        if xml_root.tag == start_tag + 'Quotation-2}Quotation':
            return self.parse_ubl_quote(xml_root)
        else:
            return super(PurchaseOrderImport, self).parse_xml_order(xml_root)

    @api.model
    def parse_ubl_quote_line(self, line, ns):
        qty_prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        line_item = line.xpath('cac:LineItem', namespaces=ns)[0]
        # line_id_xpath = line_item.xpath('cbc:ID', namespaces=ns)
        # line_id = line_id_xpath[0].text
        qty_xpath = line_item.xpath('cbc:Quantity', namespaces=ns)
        qty = float(qty_xpath[0].text)
        price_unit = 0.0
        subtotal_without_tax_xpath = line_item.xpath(
            'cbc:LineExtensionAmount', namespaces=ns)
        if subtotal_without_tax_xpath:
            subtotal_without_tax = float(subtotal_without_tax_xpath[0].text)
            if not float_is_zero(qty, precision_digits=qty_prec):
                price_unit = subtotal_without_tax / qty
        else:
            price_xpath = line_item.xpath(
                'cac:Price/cbc:PriceAmount', namespaces=ns)
            if price_xpath:
                price_unit = float(price_xpath[0].text)
        res_line = {
            'product': self.ubl_parse_product(line_item, ns),
            'qty': qty,
            'uom': {'unece_code': qty_xpath[0].attrib.get('unitCode')},
            'price_unit': price_unit,
            }
        return res_line

    @api.model
    def parse_ubl_quote(self, xml_root):
        ns = xml_root.nsmap
        main_xmlns = ns.pop(None)
        ns['main'] = main_xmlns
        date_xpath = xml_root.xpath(
            '/main:Quotation/cbc:IssueDate', namespaces=ns)
        currency_xpath = xml_root.xpath(
            '/main:Quotation/cbc:PricingCurrencyCode', namespaces=ns)
        currency_code = False
        if currency_xpath:
            currency_code = currency_xpath[0].text
        else:
            currency_xpath = xml_root.xpath(
                '//cbc:LineExtensionAmount', namespaces=ns)
            if currency_xpath:
                currency_code = currency_xpath[0].attrib.get('currencyID')
        supplier_xpath = xml_root.xpath(
            '/main:Quotation/cac:SellerSupplierParty', namespaces=ns)
        supplier_dict = self.ubl_parse_supplier_party(supplier_xpath[0], ns)
        delivery_term_xpath = xml_root.xpath(
            "/main:Quotation/cac:DeliveryTerms", namespaces=ns)
        if delivery_term_xpath:
            incoterm_dict = self.ubl_parse_incoterm(delivery_term_xpath[0], ns)
        else:
            incoterm_dict = {}
        note_xpath = xml_root.xpath(
            '/main:Quotation/cbc:Note', namespaces=ns)
        lines_xpath = xml_root.xpath(
            '/main:Quotation/cac:QuotationLine', namespaces=ns)
        res_lines = []
        for line in lines_xpath:
            res_lines.append(self.parse_ubl_quote_line(line, ns))
        # TODO : add charges
        res = {
            'partner': supplier_dict,
            'currency': {'iso': currency_code},
            'date': date_xpath[0].text,
            'incoterm': incoterm_dict,
            'note': note_xpath and note_xpath[0].text or False,
            'lines': res_lines,
        }
        # Stupid hack to remove invalid VAT of sample files
        if res['partner']['vat'] in ['DK18296799']:
            res['partner'].pop('vat')
        return res
