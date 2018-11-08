# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _get_buy_route(env):
    return env.ref(
        'purchase.route_warehouse0_buy', raise_if_not_found=False).id


def assign_route_to_rules(env):
    env.cr.execute("""
        SELECT subcontracting_service_proc_rule_id
        FROM stock_warehouse;
    """)
    wh_ids = [x[0] for x in env.cr.fetchall()]
    route = _get_buy_route(env)
    for wh in wh_ids:
        env.cr.execute("""
            UPDATE procurement_rule
            SET route_id = %s
            WHERE id = %s AND route_id IS null;
        """, (route, wh))


@openupgrade.migrate()
def migrate(env, version):
    assign_route_to_rules(env)
