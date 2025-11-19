def post_init_hook(env):
    lines_to_update = env["purchase.order.line"].search(
        [
            ("force_invoiced", "=", False),
            ("order_id.force_invoiced", "=", True),
        ]
    )
    if lines_to_update:
        lines_to_update.write({"force_invoiced": True})
    all_lines = env["purchase.order.line"].search([])
    for line in all_lines:
        line._compute_invoice_status()
