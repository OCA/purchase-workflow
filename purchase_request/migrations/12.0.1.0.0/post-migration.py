# Copyright 2018-2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from openupgradelib import openupgrade
import logging
logger = logging.getLogger(__name__)


def create_allocation(env, po_line, pr_line, stock_move_id, qty):
    vals = {'requested_product_uom_qty': qty,
            'purchase_request_line_id': pr_line,
            'purchase_line_id': po_line,
            'stock_move_id': stock_move_id,
            'allocated_product_qty': 0.0,  # this forces recalculate
            }
    alloc = env['purchase.request.allocation'].create(vals)
    return alloc


def create_service_allocation(env, po_line, pr_line, qty):
    vals = {'requested_product_uom_qty': qty,
            'purchase_request_line_id': pr_line,
            'purchase_line_id': po_line,
            }
    alloc = env['purchase.request.allocation'].create(vals)
    return alloc


def allocate_from_stock_move(env, mls, alloc_uom, ml_done=None):
    #  done here because open_product_qty is zero so cannot call method in
    #  stock_move_line
    if ml_done is None:
        ml_done = []
    for ml in mls:
        to_allocate_qty = ml.product_uom_id._compute_quantity(
            ml.qty_done, alloc_uom)
        for allocation in \
                ml.filtered(
                    lambda m: m.id not in ml_done).move_id.\
                purchase_request_allocation_ids:
            if to_allocate_qty > 0.0 and \
                    allocation.allocated_product_qty < \
                    allocation.requested_product_uom_qty:
                allocated_qty = min(
                    allocation.requested_product_uom_qty, to_allocate_qty)
                allocation.allocated_product_qty += allocated_qty
                to_allocate_qty -= allocated_qty
            ml_done.append(ml.id)
    return ml_done


def allocate_stockable(env):
    cr = env.cr
    #  First allocate stockable and consumables
    logger.info('Allocating purchase request for stockables '
                'and consumables')
    openupgrade.logged_query(cr, """
        SELECT rel.purchase_request_line_id, rel.purchase_order_line_id, sm.id,
         sm.product_qty, prl.product_qty, sm.product_uom
        FROM purchase_request_purchase_order_line_rel rel
        INNER JOIN purchase_request_line prl ON prl.id =
        rel.purchase_request_line_id
        INNER JOIN purchase_order_line pol ON pol.id =
        rel.purchase_order_line_id
        INNER JOIN product_product pp ON prl.product_id = pp.id
        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
        LEFT JOIN stock_move sm ON sm.purchase_line_id = pol.id
        WHERE pt.type != 'service'
        ORDER BY sm.create_date ASC
        """)
    res = cr.fetchall()
    ml_done = []
    for (purchase_request_line_id, purchase_order_line_id, sm_id, product_qty,
         req_qty, sm_uom_id) in res:
        purchase_request_line = env['purchase.request.line'].browse(
            purchase_request_line_id)
        sm_uom = env['uom.uom'].browse(sm_uom_id)
        alloc_uom = purchase_request_line.product_uom_id or sm_uom
        pending_qty = purchase_request_line.product_qty - \
            purchase_request_line.qty_done
        if not pending_qty:
            continue
        if sm_id:
            # we allocated what is in the stock move
            create_allocation(
                env, purchase_order_line_id, purchase_request_line_id,
                sm_id, pending_qty)
            #  cannot call super, open_qty is zero
            sm = env['stock.move'].browse(sm_id)
            if sm.state == 'done':
                ml_done = allocate_from_stock_move(env, sm.move_line_ids,
                                                   alloc_uom, ml_done)
        else:
            # we allocated what is in the PR line
            req_qty = sm_uom._compute_quantity(req_qty, alloc_uom)
            create_allocation(
                env, purchase_order_line_id, purchase_request_line_id,
                False, req_qty)
        purchase_request_line._compute_qty()


def allocate_service(env):
    cr = env.cr
    #  Allocate services
    logger.info('Allocating purchase request for services')
    openupgrade.logged_query(cr, """
        SELECT rel.purchase_request_line_id, rel.purchase_order_line_id,
         pol.product_qty, pol.product_uom
        FROM purchase_request_purchase_order_line_rel rel
        INNER JOIN purchase_request_line prl ON prl.id =
         rel.purchase_request_line_id
        INNER JOIN purchase_order_line pol ON pol.id =
        rel.purchase_order_line_id
        INNER JOIN product_product pp ON prl.product_id = pp.id
        INNER JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pt.type = 'service'
        """)
    res = cr.fetchall()
    for (purchase_request_line_id, purchase_order_line_id, product_qty,
         pol_product_uom) in res:
        purchase_request_line = env['purchase.request.line'].browse(
            purchase_request_line_id)
        product_alloc_uom = \
            purchase_request_line.product_uom_id or pol_product_uom
        pol_product_uom = env['uom.uom'].browse(pol_product_uom)
        product_alloc_qty = pol_product_uom._compute_quantity(
            product_qty, product_alloc_uom)
        alloc = create_service_allocation(
            env, purchase_order_line_id, purchase_request_line_id,
            product_alloc_qty)
        pol = env['purchase.order.line'].browse(purchase_order_line_id)
        pol.with_context(no_notify=True).update_service_allocations(0.0)
        alloc._compute_open_product_qty()
        purchase_request_line._compute_qty()


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    allocate_stockable(env)
    allocate_service(env)
