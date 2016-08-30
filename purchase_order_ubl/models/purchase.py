# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'base.ubl']

    @api.model
    def get_rfq_states(self):
        return ['draft', 'sent', 'bid']

    @api.model
    def get_order_states(self):
        return ['approved', 'except_picking', 'except_invoice', 'done']

    @api.multi
    def _ubl_add_header(self, doc_type, parent_node, ns):
        if doc_type == 'rfq':
            now_utc = fields.Datetime.now()
            date = now_utc[:10]
            time = now_utc[11:]
            currency_node_name = 'PricingCurrencyCode'
        elif doc_type == 'order':
            date = self.date_approve
            currency_node_name = 'DocumentCurrencyCode'
        ubl_version = etree.SubElement(
            parent_node, ns['cbc'] + 'UBLVersionID')
        ubl_version.text = '2.1'
        doc_id = etree.SubElement(parent_node, ns['cbc'] + 'ID')
        doc_id.text = self.name
        issue_date = etree.SubElement(parent_node, ns['cbc'] + 'IssueDate')
        issue_date.text = date
        if doc_type == 'rfq':  # IssueTime is required on RFQ, not on order
            issue_time = etree.SubElement(parent_node, ns['cbc'] + 'IssueTime')
            issue_time.text = time
        if self.notes:
            note = etree.SubElement(parent_node, ns['cbc'] + 'Note')
            note.text = self.notes
        doc_currency = etree.SubElement(
            parent_node, ns['cbc'] + currency_node_name)
        doc_currency.text = self.currency_id.name

    @api.multi
    def _ubl_add_monetary_total(self, parent_node, ns):
        monetary_total = etree.SubElement(
            parent_node, ns['cac'] + 'AnticipatedMonetaryTotal')
        line_total = etree.SubElement(
            monetary_total, ns['cbc'] + 'LineExtensionAmount',
            currencyID=self.currency_id.name)
        line_total.text = unicode(self.amount_untaxed)
        payable_amount = etree.SubElement(
            monetary_total, ns['cbc'] + 'PayableAmount',
            currencyID=self.currency_id.name)
        payable_amount.text = unicode(self.amount_total)

    @api.multi
    def _ubl_add_rfq_line(self, parent_node, oline, line_number, ns):
        line_root = etree.SubElement(
            parent_node, ns['cac'] + 'RequestForQuotationLine')
        self._ubl_add_line_item(
            line_number, oline.product_id, 'purchase', oline.product_qty,
            oline.product_uom, line_root, ns,
            seller=self.partner_id.commercial_partner_id)

    @api.multi
    def _ubl_add_order_line(self, parent_node, oline, line_number, ns):
        line_root = etree.SubElement(
            parent_node, ns['cac'] + 'OrderLine')
        dpo = self.env['decimal.precision']
        qty_precision = dpo.precision_get('Product Unit of Measure')
        price_precision = dpo.precision_get('Product Price')
        self._ubl_add_line_item(
            line_number, oline.product_id, 'purchase', oline.product_qty,
            oline.product_uom, line_root, ns,
            seller=self.partner_id.commercial_partner_id,
            currency=self.currency_id, price_subtotal=oline.price_subtotal,
            qty_precision=qty_precision, price_precision=price_precision)

    @api.multi
    def get_delivery_partner(self):
        self.ensure_one()
        if self.location_id.usage == 'customer':
            partner = self.dest_address_id
        else:
            partner = self.location_id.partner_id or self.company_id.partner_id
        return partner

    @api.multi
    def generate_rfq_ubl_xml_etree(self):
        nsmap, ns = self._ubl_get_nsmap_namespace('RequestForQuotation-2')
        xml_root = etree.Element('RequestForQuotation', nsmap=nsmap)
        doc_type = 'rfq'
        self._ubl_add_header(doc_type, xml_root, ns)

        # The order of SellerSupplierParty / BuyerCustomerParty is different
        # between RFQ and Order !
        self._ubl_add_supplier_party(
            self.partner_id, False, 'SellerSupplierParty', xml_root, ns)
        self._ubl_add_customer_party(
            False, self.company_id, 'BuyerCustomerParty', xml_root, ns)
        delivery_partner = self.get_delivery_partner()
        self._ubl_add_delivery(delivery_partner, xml_root, ns)
        if self.incoterm_id:
            self._ubl_add_delivery_terms(self.incoterm_id, xml_root, ns)

        line_number = 0
        for oline in self.order_line:
            line_number += 1
            self._ubl_add_rfq_line(xml_root, oline, line_number, ns)
        return xml_root

    @api.multi
    def generate_order_ubl_xml_etree(self):
        nsmap, ns = self._ubl_get_nsmap_namespace('Order-2')
        xml_root = etree.Element('Order', nsmap=nsmap)
        doc_type = 'order'
        self._ubl_add_header(doc_type, xml_root, ns)

        self._ubl_add_customer_party(
            False, self.company_id, 'BuyerCustomerParty', xml_root, ns)
        self._ubl_add_supplier_party(
            self.partner_id, False, 'SellerSupplierParty', xml_root, ns)
        delivery_partner = self.get_delivery_partner()
        self._ubl_add_delivery(delivery_partner, xml_root, ns)
        if self.incoterm_id:
            self._ubl_add_delivery_terms(self.incoterm_id, xml_root, ns)
        if self.payment_term_id:
            self._ubl_add_payment_terms(self.payment_term_id, xml_root, ns)
        self._ubl_add_monetary_total(xml_root, ns)

        line_number = 0
        for oline in self.order_line:
            line_number += 1
            self._ubl_add_order_line(xml_root, oline, line_number, ns)
        return xml_root

    @api.multi
    def generate_ubl_xml_string(self, doc_type):
        self.ensure_one()
        assert doc_type in ('order', 'rfq'), 'wrong doc_type'
        logger.debug('Starting to generate UBL XML %s file', doc_type)
        if doc_type == 'order':
            xml_root = self.generate_order_ubl_xml_etree()
            xsd_filename = 'UBL-Order-2.1.xsd'
        elif doc_type == 'rfq':
            xml_root = self.generate_rfq_ubl_xml_etree()
            xsd_filename = 'UBL-RequestForQuotation-2.1.xsd'
        xml_string = etree.tostring(
            xml_root, pretty_print=True, encoding='UTF-8',
            xml_declaration=True)
        self._check_xml_schema(
            xml_string, 'base_ubl/data/xsd-2.1/maindoc/' + xsd_filename)
        logger.debug(
            '%s UBL XML file generated for purchase order ID %d (state %s)',
            doc_type, self.id, self.state)
        logger.debug(xml_string)
        return xml_string

    @api.multi
    def get_ubl_filename(self, doc_type):
        """This method is designed to be inherited"""
        if doc_type == 'rfq':
            return 'UBL-RequestForQuotation-2.1.xml'
        elif doc_type == 'order':
            return 'UBL-Order-2.1.xml'

    @api.multi
    def embed_ubl_xml_in_pdf(self, pdf_content):
        self.ensure_one()
        doc_type = False
        if self.state in self.get_rfq_states():
            doc_type = 'rfq'
        elif self.state in self.get_order_states():
            doc_type = 'order'
        if doc_type:
            ubl_filename = self.get_ubl_filename(doc_type)
            xml_string = self.generate_ubl_xml_string(doc_type)
            pdf_content = self.embed_xml_in_pdf(
                xml_string, ubl_filename, pdf_content)
        return pdf_content
