# -*- coding: utf-8 -*-

from openerp.osv import fields, orm
from openerp.tools.translate import _


class PurchaseOrder(orm.Model):
    _inherit = "purchase.order"
    _columns = {
        'incoterm_address': fields.char(
            'Incoterm Place',
            help="Incoterm Place of Delivery. "
                 "International Commercial Terms are a series of "
                 "predefined commercial terms used in "
                 "international transactions."),
    }

    def onchange_dest_address_id_mod(self, cr, uid, ids, dest_address_id,
                                     warehouse_id, context=None):
        value = self.onchange_dest_address_id(cr, uid, ids, dest_address_id)
        warehouse_obj = self.pool.get('stock.warehouse')
        dest_ids = warehouse_obj.search(cr, uid,
                                        [('partner_id', '=', dest_address_id)],
                                        context=context)
        if len(dest_ids) >= 1:
            warehouse_id_ret = dest_ids[0]
            for wh in dest_ids:
                if wh == warehouse_id:
                    warehouse_id_ret = wh
        else:
            warehouse_id_ret = False
        value['value']['warehouse_id'] = warehouse_id_ret
        return value

    def onchange_dest_address_id(self, cr, uid, ids, dest_address_id):
        return super(PurchaseOrder, self).onchange_dest_address_id(
            cr, uid, ids, dest_address_id)

    def onchange_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        value = super(PurchaseOrder, self).onchange_warehouse_id(
            cr, uid, ids, warehouse_id)
        if warehouse_id:
            warehouse_obj = self.pool.get('stock.warehouse')
            dest_id = warehouse_obj.browse(cr, uid, warehouse_id,
                                           context=context).partner_id.id
            value['value']['dest_address_id'] = dest_id
            return value
        return {}
