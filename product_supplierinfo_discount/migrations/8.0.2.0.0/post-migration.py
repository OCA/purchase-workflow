# -*- coding: utf-8 -*-
# @authors: Ignacio Ibeas <ignacio@acysos.com>
# Copyright (C) 2015  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
__name__ = ("Update field price_with_disc")

def update_price(cr):
    sql = """UPDATE pricelist_partnerinfo
             SET price_with_disc = round(price * (1 - discount/100), 4)"""
    cr.execute(sql)


def migrate(cr, version):
    update_price(cr)
