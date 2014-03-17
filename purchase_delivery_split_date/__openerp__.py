# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Purchase Deliveries split by date",
    'version': '1.0',
    'author': u'Numérigraphe',
    'category': 'Purchase Management',
    'description': """
Split Purchase Deliveries in one reception per expected date
------------------------------------------------------------

When this module is installed, each Purchase Order you confirm will generate
one Reception Order per delivery date indicated in the Purchase Order Lines.

Contributors
------------

 * Philippe Rossi <pr@numerigraphe.com> (initial patch against v6.0)
 * Lionel Sausin <ls@numerigraphe.com> (modularization for v7.0)
""",
    'license': 'AGPL-3',
    "depends": ['purchase'],
}
