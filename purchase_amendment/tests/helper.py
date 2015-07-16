import pprint
import logging
_logger = logging.getLogger(__name__)


class AmendmentMixin(object):
    def _search_picking_by_product(self, product, qty):
        for picking in self.purchase.picking_ids:
            for move in picking.move_lines:
                if move.product_id == product and move.product_qty >= qty \
                        and move.state in ('confirmed', 'assigned'):
                    return picking.id

    def ship(self, cr, uid, products, context=None):
        """ Ship products of a picking

        products is a list of tuples [(product, qty)]
        """
        operations = {}
        stock_partial_picking_obj = self.registry('stock.partial.picking')
        stock_picking_obj = self.registry('stock.picking')
        picking_ids = []
        for product, qty in products:
            picking_id = self._search_picking_by_product(product, qty)
            picking_ids.append(picking_id)
            operations.setdefault(picking_id, []).append((product, qty))
        picking_ids = list(set(picking_ids))

        for picking in stock_picking_obj.browse(cr, uid, picking_ids,
                                                context=context):
            partial = []
            context.update(
                {'active_model': 'stock.picking',
                 'active_id': picking.id, 'active_ids': [picking.id]})
            for move in picking.move_lines:
                for product, qty in operations[picking.id]:
                    if move.product_id == product:
                        partial.append((0, 0, {
                            'quantity': qty,
                            'product_id': move.product_id.id,
                            'product_uom': move.product_uom.id,
                            'move_id': move.id,
                            'location_id': move.location_id.id,
                            'location_dest_id': move.location_dest_id.id,
                            'prodlot_id': move.prodlot_id.id,
                            'cost': move.product_id.standard_price
                        }))
            partial_id = stock_partial_picking_obj.create(
                cr, uid, {'move_ids': partial}, context=context)
            res = stock_partial_picking_obj.do_partial(cr, uid, [partial_id],
                                                       context=context)
            if 'res_id' in res:
                new_picking_id = res['res_id']
            else:
                new_picking_id = picking.id
            picking = stock_picking_obj.browse(cr, uid, new_picking_id,
                                               context=context)
            self.assertEqual(picking.state, 'done')

    def amend(self, cr, uid, context=None):
        amendment_obj = self.registry('purchase.order.amendment')
        context.update({
            'active_model': 'purchase.order',
            'active_id': self.purchase.id,
            'active_ids': [self.purchase.id],
        })
        amend_id = amendment_obj.create(cr, uid,
                                        {'purchase_id': self.purchase.id},
                                        context=context)
        return amendment_obj.browse(cr, uid, amend_id, context=context)

    def amend_product(self, cr, uid, amendment, product, qty, \
                                               context=None):
        amendment_item_obj = self.registry('purchase.order.amendment.item')
        amendment_obj = self.registry('purchase.order.amendment')
        for item in amendment.item_ids:
            if item.purchase_line_id.product_id == product and item.state \
                    not in ('cancel', 'done'):
                amendment_item_obj.write(cr, uid, [item.id], {'new_qty': qty},
                                         context=context)
        return amendment_obj.browse(cr, uid, amendment.id,
                                         context=context)


    def assertRecordEqual(self, expected, actual, msg=None):
        for field_name, expected_value in expected.iteritems():
            self.assertEqual(actual[field_name], expected_value, msg)

    def check_record_equal(self, expected, actual):
        try:
            self.assertRecordEqual(expected, actual)
        except AssertionError:
            return False
        return True

    def assertRecordsetEqual(self, expecteds, actual_records, msg=None):
        not_found = []
        extra_actual = []
        for actual_record in actual_records:
            extra_actual.append(actual_record.id)

        diffMsg = ''

        for expected in expecteds:
            for actual_record in actual_records:
                if self.check_record_equal(expected, actual_record):
                    extra_actual = list(set(extra_actual) -
                                        {actual_record.id})
                    break
            else:
                not_found.append(expected)

        for item in not_found:
            diffMsg += ("- %s\n" % pprint.pformat(item))

        for item in actual_records:
            if item.id in extra_actual:
                extra_values = {k: item[k] for k in expecteds[0].keys()}
                diffMsg += ("+ %s\n" % pprint.pformat(extra_values))

        if diffMsg:
            standardMsg = '\nLines do not match:\n'
            standardMsg = self._truncateMessage(standardMsg, diffMsg)
            msg = self._formatMessage(msg, standardMsg)
            self.fail(msg)

    def assert_amendment_items(self, cr, uid, items, expected_lines,
                               context=None):
        expecteds = [{
            'product_id': exp[0],
            'original_qty': exp[1],
            'new_qty': exp[2],
            'state': exp[3],
        } for exp in expected_lines]
        self.assertRecordsetEqual(expecteds, items)

    def assert_purchase_lines(self, cr, uid, expected_lines, context=None):
        order_lines = []
        for order_line in self.purchase.order_line:
            order_lines.append(order_line)
        expecteds = [{
            'product_id': exp[0],
            'product_qty': exp[1],
            'state': exp[2],
        } for exp in expected_lines]
        self.assertRecordsetEqual(expecteds, order_lines)

    def assert_moves(self, cr, uid, expected_moves, context=None):
        moves = []
        picking_obj = self.registry('stock.picking.in')
        picking_ids = picking_obj.search(
            cr, uid, [('purchase_id', '=', self.purchase.id)], context=context)
        for picking in picking_obj.browse(cr, uid, picking_ids,
                                          context=context):
            for move in picking.move_lines:
                moves.append(move)
        expecteds = [{
            'product_id': exp[0],
            'product_qty': exp[1],
            'state': exp[2],
        } for exp in expected_moves]

        self.assertRecordsetEqual(expecteds, moves)
