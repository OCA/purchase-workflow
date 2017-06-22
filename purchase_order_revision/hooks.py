# -*- coding: utf-8 -*-
# Copyright 2013 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
# Copyright 2015 Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    """ Fill unrevisioned name of all existent purchases """
    query = """
        UPDATE purchase_order SET unrevisioned_name=name
        WHERE unrevisioned_name IS NULL;
    """
    cr.execute(query)
