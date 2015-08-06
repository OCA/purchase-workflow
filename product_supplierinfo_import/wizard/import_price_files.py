# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import fields, models, api, exceptions, _
import base64
import cStringIO
import tempfile
import csv


class ImportPriceFile(models.TransientModel):
    _name = 'import.price.file'
    _description = 'Import Price List File'

    data = fields.Binary('File', required=True)
    name = fields.Char('Filename', required=False)
    delimeter = fields.Char('Delimeter', default=',',
                            help='Default delimeter is ","')
    file_type = fields.Selection([('csv', 'CSV'), ('xls', 'XLS')], 'File Type',
                                 required=True, default='csv')

    def _prepare_data_dict(self, data_dict):
        return data_dict

    def _import_csv(self, load_id, file_data, delimeter=';'):
        """ Imports data from a CSV file in defined object.
        @param load_id: Loading id
        @param file_data: Input data to load
        @param delimeter: CSV file data delimeter
        @return: Imported file number
        """
        file_line_obj = self.env['product.supplierinfo.load.line']
        data = base64.b64decode(file_data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        reader_info = []
        reader = csv.reader(file_input, delimiter=str(delimeter),
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]
        counter = 0
        if not isinstance(keys, list):
            raise exceptions.Warning(_("Not a valid file!"))
        del reader_info[0]
        for i in range(len(reader_info)):
            field = reader_info[i]
            values = dict(zip(keys, field))
            data_dict = self._prepare_data_dict(
                {'supplier': 'Supplier' in values and values['Supplier'],
                 'code': 'ProductCode' in values and values['ProductCode'],
                 'sequence': 'Sequence' in values and values['Sequence'],
                 'supplier_code': 'ProductSupplierCode' in values and
                 values['ProductSupplierCode'],
                 'info': 'ProductSupplierName' in values and
                 values['ProductSupplierName'],
                 'delay': 'Delay' in values and values['Delay'],
                 'price': 'Price' in values and
                    values['Price'].replace(',', '.'),
                 'min_qty': 'MinQty' in values and values['MinQty'],
                 'fail': True,
                 'fail_reason': _('No Processed'),
                 'file_load': load_id})
            file_line_obj.create(data_dict)
            counter += 1
        return counter

    def _import_xls(self, load_id, file_data):
        """ Imports data from a XLS file in defined object.
        @param load_id: Loading id
        @param file_data: Input data to load
        @return: Imported file number
        """
        try:
            import xlrd
        except ImportError:
            exceptions.Warning(_("xlrd python lib  not installed"))
        file_line_obj = self.env['product.supplierinfo.load.line']
        file_1 = base64.decodestring(file_data)
        (fileno, fp_name) = tempfile.mkstemp('.xls', 'openerp_')
        openfile = open(fp_name, "w")
        openfile.write(file_1)
        book = xlrd.open_workbook(fp_name)
        sheet = book.sheet_by_index(0)
        values = {}
        keys = sheet.row_values(0, 0, end_colx=sheet.ncols)
        for counter in range(sheet.nrows - 1):
            # grab the current row
            rowValues = sheet.row_values(counter + 1, 0,
                                         end_colx=sheet.ncols)
            row_lst = []
            for val in rowValues:  # codification format control
                if isinstance(val, unicode):
                    valor = val.encode('utf8')
                    row_lst.append(valor)
                elif isinstance(val, float):
                    if float(val) % 1 == 0.0:
                        row_lst.append(
                            '{0:.5f}'.format(float(val)).split('.')[0])
                    else:
                        row_lst.append('{0:g}'.format(float(val)))
                else:
                    row_lst.append(val)
            row = map(lambda x: str(x), row_lst)
            values = dict(zip(keys, row))
            data_dict = self._prepare_data_dict(
                {'supplier': 'Supplier' in values and values['Supplier'],
                 'code': 'ProductCode' in values and values['ProductCode'],
                 'sequence': 'Sequence' in values and values['Sequence'],
                 'supplier_code': 'ProductSupplierCode' in values and
                 values['ProductSupplierCode'],
                 'info': 'ProductSupplierName' in values and
                 values['ProductSupplierName'],
                 'delay': 'Delay' in values and values['Delay'],
                 'price': 'Price' in values and
                 values['Price'].replace(',', '.'),
                 'min_qty': 'MinQty' in values and values['MinQty'],
                 'fail': True,
                 'fail_reason': _('No Processed'),
                 'file_load': load_id
                 })
            file_line_obj.create(data_dict)
            counter += 1
        return counter

    @api.multi
    def action_import(self):
        file_load_obj = self.env['product.supplierinfo.load']
        context = self._context
        if 'active_id' in context:
            load_id = context['active_id']
            file_load = file_load_obj.browse(load_id)
        for line in file_load.file_lines:
            line.unlink()
        for wiz in self:
            if not wiz.data:
                raise exceptions.Warning(_("You need to select a file!"))
            date_hour = fields.datetime.now()
            actual_date = fields.date.today()
            filename = wiz.name
            if wiz.file_type == 'csv':
                counter = self._import_csv(load_id, wiz.data, wiz.delimeter)
            elif wiz.file_type == 'xls':
                counter = self._import_xls(load_id, wiz.data)
            else:
                raise exceptions.Warning(_("Not a .csv/.xls file found"))
            file_load.write({'name': ('%s_%s') % (filename, actual_date),
                             'date': date_hour, 'fails': counter,
                             'file_name': filename, 'process': counter})
        return counter
