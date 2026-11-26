# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    """Core already has the column, so the install does not compute it."""
    env["purchase.requisition.line"].search(
        [("product_id", "!=", False), ("name", "=", False)]
    )._compute_name()
