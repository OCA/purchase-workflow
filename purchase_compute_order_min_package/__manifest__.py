##############################################################################
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
#
##############################################################################

{
    'name': 'Computed Purchase Order by Min. Nb of Package',
    'version': '12.0.1.0.1',
    'description': 'Computed Purchase Order by Min. Nb of Package',
    'category': 'Purchase',
    'author': 'Trobz',
    'website': 'http://www.trobz.com',
    'license': 'AGPL-3',
    'depends': [
        'purchase_compute_order',
    ],
    'data': [
        'views/product_supplierinfo_view.xml',
    ],
}
