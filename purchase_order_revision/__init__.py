# -*- coding: utf-8 -*-

from . import model


def fill_unrevisioned_name(cr, registry):
    cr.execute("UPDATE purchase_order set unrevisioned_name=name "
               "WHERE unrevisioned_name IS NULL")
