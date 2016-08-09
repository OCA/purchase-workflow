# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp.report import report_sxw


def formatLang(env, value, digits=None, grouping=True, monetary=False,
               dp=False, currency_obj=False):
    rml_parser = report_sxw.rml_parse(
        env.cr, env.uid, 'format_lang_wrapper', context=env.context)
    return rml_parser.formatLang(
        value, digits=digits, grouping=grouping, monetary=monetary, dp=dp,
        currency_obj=currency_obj)
