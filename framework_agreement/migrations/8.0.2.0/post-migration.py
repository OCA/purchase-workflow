# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


def migrate(cr, installed_version):
    """Add missing portfolios to agreements, create them if necessary."""
    cr.execute('SELECT a.id, a.supplier_id, p.name '
               'FROM framework_agreement a '
               'JOIN res_partner p '
               'ON a.supplier_id = p.id '
               'WHERE portfolio_id is null;')

    for agreement_id, supplier_id, supplier_name in cr.fetchall():
        cr.execute(
            'SELECT id '
            'FROM framework_agreement_portfolio '
            'WHERE supplier_id = %s;',
            (supplier_id,),
        )
        portfolios = cr.fetchone()
        if portfolios:
            new_portfolio = portfolios[0]
        else:
            cr.execute('INSERT INTO framework_agreement_portfolio '
                       '(name, supplier_id) '
                       'VALUES (%s, %s) '
                       'RETURNING id; ',
                       (supplier_name, supplier_id))
            new_portfolio = cr.fetchone()[0]

        cr.execute('UPDATE framework_agreement '
                   'SET portfolio_id = %s '
                   'WHERE id = %s',
                   (new_portfolio, agreement_id),
                   )
