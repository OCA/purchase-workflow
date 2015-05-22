import pprint


class AmendmentMixin(object):
    def _search_picking_by_product(self, product, qty):
        return self.purchase.picking_ids.filtered(
            lambda p: any(move.product_id == product and
                          move.product_qty >= qty and
                          move.state in ('confirmed', 'assigned')
                          for move in p.move_lines)
        )[0]

    def ship(self, products=None):
        """ Ship products of a picking

        products is a list of tuples [(product, qty)]
        """
        operations = {}
        pickings = self.env['stock.picking'].browse()
        if products:
            for product, qty in products:
                picking = self._search_picking_by_product(product, qty)
                pickings |= picking
                operations.setdefault(picking, []).append((product, qty))
        else:
            # ship all
            pickings = self.purchase.picking_ids.filtered(
                lambda p: p.state not in ('cancel', 'done')
            )
            for picking in pickings:
                operations[picking] = []

        pickings.do_prepare_partial()

        for picking, product_qtys in operations.iteritems():
            for (product, qty) in product_qtys:
                pack_operation = picking.pack_operation_ids.filtered(
                    lambda p: p.product_id == product
                )
                pack_operation.product_qty = qty
        pickings.do_transfer()
        for picking in pickings:
            self.assertEqual(picking.state, 'done')

    def split(self, products):
        """ Split pickings

        ``products`` is a list of tuples [(product, quantity)]
        """
        operations = {}
        pickings = self.env['stock.picking'].browse()
        for product, qty in products:
            picking = self._search_picking_by_product(product, qty)
            pickings |= picking
            operations.setdefault(picking, []).append((product, qty))

        location_stock = self.env.ref('stock.stock_location_stock')
        location_customer = self.env.ref('stock.stock_location_customers')

        for picking in pickings:
            transfer_model = self.env['stock.transfer_details'].with_context(
                active_model='stock.picking',
                active_id=picking.id,
                active_ids=picking.ids
            )
            items = []
            for product_qtys in operations[picking]:
                items.append((0, 0, {
                    'quantity': qty,
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'sourceloc_id': location_stock.id,
                    'destinationloc_id': location_customer.id,
                }))
            transfer = transfer_model.create({
                'picking_id': picking.id,
                'item_ids': items
            })
            transfer.with_context(do_only_split=True).do_detailed_transfer()

    def cancel_move(self, product, qty):
        move = self.purchase.mapped('picking_ids.move_lines').filtered(
            lambda m: (m.product_id == product and
                       m.product_qty == qty and
                       m.state in ('confirmed', 'assigned'))
        )
        move.action_cancel()

    def amend(self):
        return self.amendment_model.with_context(
            active_model='purchase.order',
            active_id=self.purchase.id,
            active_ids=self.purchase.ids,
        ).create({'purchase_id': self.purchase.id})

    def amend_product(self, amendment, product, qty):
        item = amendment.item_ids.filtered(
            lambda i: i.purchase_line_id.product_id == product
            and i.state not in ('cancel', 'done')
        )

        item.new_qty = qty

    def assert_amendment_quantities(self, amendment, product,
                                    ordered_qty=0, received_qty=0,
                                    canceled_qty=0, amend_qty=0):
        item = amendment.item_ids.filtered(
            lambda i: i.purchase_line_id.product_id == product
        )
        group = item.read_group(
            domain=[('id', 'in', item.ids)],
            fields=['purchase_line_id', 'amend_qty', 'received_qty',
                    'canceled_qty', 'ordered_qty'],
            groupby=['purchase_line_id']
        )
        self.assertEqual(len(group), 1)
        group = group[0]
        self.assertEqual(
            [group['ordered_qty'], group['received_qty'],
             group['canceled_qty'], group['amend_qty']],
            [ordered_qty, received_qty,
             canceled_qty, amend_qty],
            'The quantities do not match (ordered, received, '
            'canceled, amended)'
        )

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
        extra_actual = actual_records

        diffMsg = ''

        for expected in expecteds:
            for actual_record in actual_records:
                if self.check_record_equal(expected, actual_record):
                    extra_actual -= actual_record
                    break
            else:
                not_found.append(expected)

        for item in not_found:
            diffMsg += ("- %s\n" % pprint.pformat(item))
        for item in extra_actual:
            extra_values = {k: item[k] for k in expecteds[0].keys()}
            diffMsg += ("+ %s\n" % pprint.pformat(extra_values))

        if diffMsg:
            standardMsg = '\nLines do not match:\n'
            standardMsg = self._truncateMessage(standardMsg, diffMsg)
            msg = self._formatMessage(msg, standardMsg)
            self.fail(msg)

    def assert_purchase_lines(self, expected_lines):
        lines = self.purchase.order_line
        not_found = []
        for product, qty, state in expected_lines:
            for line in lines:
                if ((line.product_id, line.product_qty, line.state) ==
                        (product, qty, state)):
                    lines -= line
                    break
            else:
                not_found.append((product, qty, state))
        message = ''
        for product, qty, state in not_found:
            message += ("- product: '%s', qty: '%s', state: '%s'\n" %
                        (product.display_name, qty, state))
        for line in lines:
            message += ("+ product: '%s', qty: '%s', state: '%s'\n" %
                        (line.product_id.display_name, line.product_qty,
                         line.state))
        if message:
            raise AssertionError('Purchase lines do not match:\n\n%s' %
                                 message)

    def assert_moves(self, expected_moves):
        moves = self.purchase.mapped('picking_ids.move_lines')
        not_found = []
        for product, qty, state in expected_moves:
            for move in moves:
                if ((move.product_id, move.product_qty, move.state) ==
                        (product, qty, state)):
                    moves -= move
                    break
            else:
                not_found.append((product, qty, state))
        message = ''
        for product, qty, state in not_found:
            message += ("- product: '%s', qty: '%s', state: '%s'\n" %
                        (product.display_name, qty, state))
        for line in moves:
            message += ("+ product: '%s', qty: '%s', state: '%s'\n" %
                        (line.product_id.display_name, line.product_qty,
                         line.state))
        if message:
            raise AssertionError('Moves do not match:\n\n%s' % message)
