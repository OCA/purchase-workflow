# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2013 Camptocamp SA
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
"""Provides basic mechanism to unify the way records are transformed into
other records

"""

from openerp.osv import orm


class BrowseAdapterSourceMixin(object):
    """Mixin class used by Model that are transformation sources"""

    def _company(self, cr, uid, context):
        """Return company id

        :returns: company id

        """
        return self.pool['res.company']._company_default_get(cr, uid, 'purchase.order',
                                                             context=context)

    def _direct_map(self, line, mapping, context=None):
        """Take a dict of left key right key and make direct mapping
        into the model

        :returns: data dict ready to be used
        """
        data = {}
        for po_key, source_key in mapping.iteritems():
            value = line[source_key]
            if isinstance(value, orm.browse_record):
                value = value.id
            elif isinstance(value, orm.browse_null):
                value = False
            elif isinstance(value, orm.browse_record_list):
                raise NotImplementedError('List are not supported in direct map')

            data[po_key] = value
        return data


class BrowseAdapterMixin(object):

    def _do_checks(self, cr, uid, model, data, context=None):
        """Perform validation check of adapted data.

        All missing or incorrect values are return at once.

        :returns: array of exceptions

        """
        required_keys = set(k for k, v in model._columns.iteritems()
                                if v.required and not getattr(v, '_fnct', False))
        empty_required = set(x for x in data
                                if x in required_keys and not data[x])
        missing_required = required_keys - set(data.keys())
        missing_required.update(empty_required)
        if missing_required:
            return[ValueError('Following value are missing or False'
                              ' while adapting %s: %s' %
                                  (model._name, ", ".join(missing_required)))]
        return []

    def _validate_adapted_data(self, cr, uid, model, data, context=None):
        """Perform validation check of adapted data.

        All missing or incorrect values are return at once.

        :returns: validated data or raise Value error

        """
        errors = self._do_checks(cr, uid, model, data, context=context)
        if errors:
            raise ValueError('Data are invalid for following reason %s' %
                                 ("\n".join(repr(e) for e in errors)))
        return data

    def _adapt_origin(self, cr, uid, model, origin,
                      map_fun, post_fun=None, context=None, **kwargs):
        """Do transformation of source data to dest data using transforms function.

        :param origin: source record
        :param map_fun: transform function
        :param post_fun: post transformation hook function

        :returns: transformed data

        """
        if not callable(map_fun):
            raise ValueError('Mapping function is not callable')
        if post_fun and not callable(post_fun):
            raise ValueError('Post hook function is not callable')
        data = map_fun(cr, uid, origin, context=context, **kwargs)
        # we complete with default
        missing = set(model._columns.keys()) - set(data.keys())
        data.update(model.default_get(cr, uid, missing, context=context))
        return data
