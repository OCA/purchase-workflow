# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.tools import float_is_zero
from openerp.exceptions import Warning as UserError
import logging
import mimetypes
from lxml import etree

logger = logging.getLogger(__name__)


class PurchaseOrderImport(models.TransientModel):
    _name = 'purchase.order.import'
    _description = 'Purchase Order Import from Files'

    @api.model
    def _get_purchase_id(self):
        assert self._context['active_model'] == 'purchase.order',\
            'bad active_model'
        return self.env['purchase.order'].browse(self._context['active_id'])

    quote_file = fields.Binary(
        string='XML or PDF Quotation', required=True,
        help="Upload a quotation file that you received from "
        "your supplier. Supported formats: XML and PDF "
        "(PDF with an embeded XML file).")
    quote_filename = fields.Char(string='Filename')
    update_option = fields.Selection([
        ('price', 'Price'),
        ('all', 'Price and Quantity'),
        ], default='price', string='Update Option', required=True)
    purchase_id = fields.Many2one(
        'purchase.order', string='RFQ to Update', default=_get_purchase_id,
        readonly=True)

    @api.model
    def parse_xml_quote(self, xml_root):
        raise UserError(_(
            "This type of XML quotation is not supported. Did you install "
            "the module to support this XML format?"))

    @api.model
    def parse_pdf_quote(self, quote_file):
        """
        Get PDF attachments, filter on XML files and call import_order_xml
        """
        xml_files_dict = self.get_xml_files_from_pdf(quote_file)
        if not xml_files_dict:
            raise UserError(_(
                'There are no embedded XML file in this PDF file.'))
        for xml_filename, xml_root in xml_files_dict.iteritems():
            logger.info('Trying to parse XML file %s', xml_filename)
            try:
                parsed_quote = self.parse_xml_quote(xml_root)
                return parsed_quote
            except:
                continue
        raise UserError(_(
            "This type of XML quotation is not supported. Did you install "
            "the module to support this XML format?"))

    # Format of parsed_quote
    # {
    # 'partner': {
    #     'vat': 'FR25499247138',
    #     'name': 'Camptocamp',
    #     'email': 'luc@camptocamp.com',
    #     },
    # 'currency': {'iso': 'EUR', 'symbol': u'€'},
    # 'incoterm': 'EXW',
    # 'note': 'some notes',
    # 'chatter_msg': ['msg1', 'msg2']
    # 'lines': [{
    #           'product': {
    #                'code': 'EA7821',
    #                'ean13': '2100002000003',
    #                },
    #           'qty': 2.5,
    #           'uom': {'unece_code': 'C62'},
    #           'price_unit': 12.42,  # without taxes
    #    }]

    @api.model
    def parse_quote(self, quote_file, quote_filename):
        assert quote_file, 'Missing quote file'
        assert quote_filename, 'Missing quote filename'
        filetype = mimetypes.guess_type(quote_filename)[0]
        logger.debug('Quote file mimetype: %s', filetype)
        if filetype == 'application/xml':
            try:
                xml_root = etree.fromstring(quote_file)
            except:
                raise UserError(_("This XML file is not XML-compliant"))
            pretty_xml_string = etree.tostring(
                xml_root, pretty_print=True, encoding='UTF-8',
                xml_declaration=True)
            logger.debug('Starting to import the following XML file:')
            logger.debug(pretty_xml_string)
            parsed_quote = self.parse_xml_quote(xml_root)
        elif filetype == 'application/pdf':
            parsed_quote = self.parse_pdf_quote(quote_file)
        else:
            raise UserError(_(
                "This file '%s' is not recognised as XML nor PDF file. "
                "Please check the file and it's extension.") % quote_filename)
        logger.debug('Result of quotation parsing: %s', parsed_quote)
        if 'attachments' not in parsed_quote:
            parsed_quote['attachments'] = {}
        parsed_quote['attachments'][quote_filename] =\
            quote_file.encode('base64')
        if 'chatter_msg' not in parsed_quote:
            parsed_quote['chatter_msg'] = []
        return parsed_quote

    @api.model
    def _prepare_update_order_vals(self, parsed_quote, order):
        vals = {}
        incoterm = self.env['business.document.import']._match_incoterm(
            parsed_quote.get('incoterm'), parsed_quote['chatter_msg'])
        if incoterm and incoterm != order.incoterm_id:
            parsed_quote['chatter_msg'].append(_(
                "The incoterm has been updated from %s to %s upon import "
                "of the quotation file '%s'") % (
                order.incoterm_id.code, incoterm.code,
                self.quote_filename))
            vals['incoterm_id'] = incoterm.id
        return vals

    @api.model
    def _prepare_create_order_line(
            self, product, qty, uom, price_unit, so_vals):
        vals = {
            'product_id': product.id,
            'product_qty': qty,
            'product_uom': uom.id,
            'price_unit': price_unit,  # TODO fix
        }
        return vals

    @api.multi
    def update_order_lines(self, parsed_quote, order):
        polo = self.env['purchase.order.line']
        chatter = parsed_quote['chatter_msg']
        dpo = self.env['decimal.precision']
        bdio = self.env['business.document.import']
        qty_prec = dpo.precision_get('Product Unit of Measure')
        existing_lines = []
        for oline in order.order_line:
            price_unit = 0.0
            if not float_is_zero(
                    oline.product_qty, precision_digits=qty_prec):
                price_unit = oline.price_subtotal / float(oline.product_qty)
            existing_lines.append({
                'product': oline.product_id,
                'name': oline.name,
                'qty': oline.product_qty,
                'uom': oline.product_uom,
                'price_unit': price_unit,
                'line': oline,
                })

        compare_res = bdio.compare_lines(
            existing_lines, parsed_quote['lines'], chatter,
            seller=order.partner_id.commercial_partner_id)

        update_option = self.update_option
        for oline, cdict in compare_res['to_update'].iteritems():
            write_vals = {}
            if cdict.get('price_unit'):
                chatter.append(_(
                    "The unit price has been updated on the RFQ line with "
                    "product '%s' from %s to %s %s.") % (
                        oline.product_id.name_get()[0][1],
                        cdict['price_unit'][0], cdict['price_unit'][1],
                        order.currency_id.name))
                write_vals['price_unit'] = cdict['price_unit'][1]  # TODO
            if update_option == 'all' and cdict.get('qty'):
                chatter.append(_(
                    "The quantity has been updated on the RFQ line with "
                    "product '%s' from %s to %s %s.") % (
                        oline.product_id.name_get()[0][1],
                        cdict['qty'][0], cdict['qty'][1],
                        oline.product_uom.name))
            if write_vals:
                oline.write(write_vals)
        if compare_res['to_remove']:  # we don't delete the lines, only warn
            warn_label = [
                '%s %s x %s' % (
                    l.product_qty, l.product_uom.name, l.product_id.name)
                for l in compare_res['to_remove']]
            chatter.append(_(
                "%d order line(s) are not in the imported quotation: %s") % (
                    len(compare_res['to_remove']),
                    ', '.join(warn_label)))
        if compare_res['to_add']:
            to_create_label = []
            for add in compare_res['to_add']:
                line_vals = self._prepare_create_order_line(
                    add['product'], add['uom'], add['import_line'],
                    order)
                line_vals['order_id'] = order.id
                new_line = polo.create(line_vals)
                to_create_label.append('%s %s x %s' % (
                    new_line.product_qty,
                    new_line.product_uom.name,
                    new_line.name))
            chatter.append(_("%d new order line(s) created: %s") % (
                len(compare_res['to_add']), ', '.join(to_create_label)))
        return True

    @api.model
    def _prepare_create_order_line(self, product, uom, import_line, order):
        polo = self.env['purchase.order.line']
        product_change_res = polo.onchange_product_id(
            order.pricelist_id.id, product.id,
            import_line['qty'], uom.id,
            order.partner_id.id,
            fiscal_position_id=order.fiscal_position.id or False,
            price_unit=import_line['price_unit'])['value']
        if product_change_res.get('taxes_id'):
            product_change_res['taxes_id'] = [
                (6, 0, product_change_res['taxes_id'])]
        vals = product_change_res
        vals['product_id'] = product.id
        return vals

    @api.multi
    def update_rfq_button(self):
        self.ensure_one()
        bdio = self.env['business.document.import']
        order = self.purchase_id
        assert order, 'No link to PO'
        if not order:
            raise UserError(_('You must select a quotation to update.'))
        parsed_quote = self.parse_quote(
            self.quote_file.decode('base64'), self.quote_filename)
        currency = bdio._match_currency(
            parsed_quote.get('currency'), parsed_quote['chatter_msg'])
        partner = bdio._match_partner(
            parsed_quote['partner'], parsed_quote['chatter_msg'],
            partner_type='supplier')
        if (
                partner.commercial_partner_id !=
                order.partner_id.commercial_partner_id):
            raise UserError(_(
                "The supplier of the imported quotation (%s) is different "
                "from the supplier of the RFQ (%s)." % (
                    partner.commercial_partner_id.name,
                    order.partner_id.commercial_partner_id.name)))
        if currency != order.currency_id:
            raise UserError(_(
                "The currency of the imported quotation (%s) is different "
                "from the currency of the RFQ (%s)") % (
                currency.name, order.currency_id.name))
        vals = self._prepare_update_order_vals(parsed_quote, order)
        if vals:
            order.write(vals)
        if not parsed_quote.get('lines'):
            raise UserError(_(
                "This quotation doesn't have any line !"))
        self.update_order_lines(parsed_quote, order)
        bdio.post_create_or_update(parsed_quote, order)
        logger.info(
            'purchase.order ID %d updated via import of file %s', order.id,
            self.quote_filename)
        order.message_post(_(
            "This RFQ has been updated automatically via the import of "
            "quotation file %s") % self.quote_filename)
        return True
