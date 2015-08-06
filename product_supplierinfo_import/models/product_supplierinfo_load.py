# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, exceptions, api, _


class ProductSupplierinfoLoad(models.Model):
    _name = 'product.supplierinfo.load'
    _description = 'Product Price List Load'

    name = fields.Char('Load')
    date = fields.Date('Date:', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    file_lines = fields.One2many('product.supplierinfo.load.line', 'file_load',
                                 'Product Price List Lines')
    fails = fields.Integer('Fail Lines:', readonly=True)
    process = fields.Integer('Lines to Process:', readonly=True)
    supplier = fields.Many2one('res.partner', help="If there is no supplier "
                               "defined in line this will be used")

    def _get_supplierinfo_data(self, supplier_id, product_tmpl_id):
        """ returns supplierinfo data
        @param supplier: supplier
        @param product_tmp: product template
        @return: supplierinfo_id and pricelist_id in a dictionary
        """
        res = {}
        if supplier_id and product_tmpl_id:
            psupplinfo_obj = self.env['product.supplierinfo']
            pricepinfo_obj = self.env['pricelist.partnerinfo']
            psupplinfos = psupplinfo_obj.search(
                [('name', '=', supplier_id),
                 ('product_tmpl_id', '=', product_tmpl_id)])
            if psupplinfos:
                res = {'supplierinfo_id': psupplinfos[0].id}
                priceinfo = pricepinfo_obj.search(
                    [('suppinfo_id', '=', psupplinfos[0].id)])
                if priceinfo[0]:
                    res['pricelist_id'] = priceinfo[0]
        return res

    @api.multi
    def process_lines(self):
        for file_load in self:
            partner_obj = self.env['res.partner']
            product_obj = self.env['product.product']
            psupplinfo_obj = self.env['product.supplierinfo']
            pricepinfo_obj = self.env['pricelist.partnerinfo']
            if not file_load.file_lines:
                raise exceptions.Warning(
                    _("There must be one line at least to process"))
            for line in [x for x in file_load.file_lines if x.fail and x.code]:
                # process fail lines and search product code
                products = product_obj.search(
                    [('default_code', '=', line.code)])
                supplier = file_load.supplier
                if line.supplier:
                    supplier_lst = partner_obj.search(
                        ['|', ('ref', '=', line.supplier),
                         ('name', "=", line.supplier)])
                    if supplier_lst:
                        supplier = supplier_lst[0]
                if not supplier:
                    line.fail_reason = _('Supplier not found')
                    continue
                if products and supplier:
                    supinfo_data = self._get_supplierinfo_data(
                        supplier.id, products[0].product_tmpl_id.id)
                    if 'suppinfo_id' in supinfo_data:  # update
                        suppinfo = psupplinfo_obj.browse(
                            supinfo_data['suppinfo_id'])
                        suppinfo.sequence = line.sequence or None
                        suppinfo.product_code = line.supplier_code or None
                        suppinfo.product_name = line.info or None
                        suppinfo.min_qty = line.min_qty or 1
                        suppinfo.delay = line.delay or 1
                        if 'pricelist_id' in supinfo_data:
                            pricelist = pricepinfo_obj.browse(
                                supinfo_data['pricelist_id'])
                            pricelist.price = line.price
                            pricelist.min_quantity = line.min_qty
                    else:
                        psupplinfo = psupplinfo_obj.create(
                            {'name': supplier.id,
                             'product_tmpl_id': products[0].product_tmpl_id.id,
                             'sequence': line.sequence or None,
                             'product_code': line.supplier_code or None,
                             'product_name': line.info or None,
                             'min_qty': line.min_qty,
                             'delay': line.delay or None
                             })
                        pricepinfo_obj.create(
                            {'suppinfo_id': psupplinfo.id,
                             'min_quantity': psupplinfo.min_qty,
                             'price': line.price})
                    file_load.fails -= 1
                    line.write({'fail': False,
                                'fail_reason': _('Correctly Processed')})
                else:
                    line.fail_reason = _('Product not found')
        return True


class ProductSupplierinfoLoadLine(models.Model):
    _name = 'product.supplierinfo.load.line'
    _description = 'Product Price List Load Line'

    supplier = fields.Char('Supplier')
    code = fields.Char('Product Code', required=True)
    sequence = fields.Integer('Sequence')
    supplier_code = fields.Char('Supplier Code')
    info = fields.Char('Product Description')
    delay = fields.Integer('Delivery Lead Time')
    price = fields.Float('Product Price', required=True)
    min_qty = fields.Float('Minimal Quantity')
    fail = fields.Boolean('Fail')
    fail_reason = fields.Char('Fail Reason')
    file_load = fields.Many2one('product.supplierinfo.load', 'Load',
                                required=True)
