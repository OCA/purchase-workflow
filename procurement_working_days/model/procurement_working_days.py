# -*- coding: utf8 -*-
#
# Copyright (C) 2014 NDP Systèmes (<http://www.ndp-systemes.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from datetime import datetime

from openerp import fields, models, api, _
from openerp.exceptions import except_orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class res_company_with_calendar(models.Model):
    _inherit = "res.company"

    calendar_id = fields.Many2one("resource.calendar", "Company default calendar",
                                  help="The default calendar of the company to define working days. This calendar is "
                                       "used for locations outside warehouses or "
                                       "for warehouses without a calendar defined. If undefined here the default "
                                       "calendar will consider working days being Monday to Friday.")


class stock_warehouse_with_calendar(models.Model):
    _inherit = "stock.warehouse"

    resource_id = fields.Many2one("resource.resource", "Warehouse resource",
                                  help="The resource is used to define the working days of the warehouse. If undefined "
                                       "the system will fall back to the default company calendar.")


class res_partner_with_calendar(models.Model):
    _inherit = "res.partner"

    resource_id = fields.Many2one("resource.resource", "Supplier resource",
                                  help="The supplier resource is used to define the working days of the supplier when "
                                       "calculating lead times. If undefined here the system will consider working "
                                       "days of the supplier being Monday to Friday.")


class procurement_working_days(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _schedule_working_days(self, days, day_date, resource, calendar):
        """Wrapper to call resource.calendar.schedule_days_get_date.

        :param int days: number of days to schedule. Negative if backwards
        :param datetime day_date: date to start scheduling from
        :param record resource_id: resource to calculate specific leaves. If false, only general leaves are counted
        :param record calendar: calendar to schedul on
        :rtype datetime
        """
        if calendar:
            newdate = calendar.schedule_days_get_date(days, day_date=day_date, resource_id=resource.id,
                                                      compute_leaves=True)
        else:
            raise except_orm(_("No calendar found!"),_("No calendar has been found to compute scheduling."))
        # For some reason call with new api returns a list of 1 date instead of the date
        if isinstance(newdate, (list, tuple)):
            newdate = newdate[0]
        return newdate

    def _get_move_calendar(self):
        """Returns the applicable (calendar, resource) tuple to use for stock move delay.
        The applicable calendar is the calendar of the warehouse resource if the location is in a warehouse and this
        warehouse has a resource, otherwise the company default calendar if it exists or the module's default calendar
        which considers workings days as being Monday to Friday.
        The applicable resource is the warehouse's resource if defined."""
        if self.location_id:
            warehouse_id = self.location_id.get_warehouse(self.location_id)
        else:
            warehouse_id = self.warehouse_id
        calendar_id = False
        resource_id = warehouse_id and warehouse_id.resource_id
        if resource_id:
            calendar_id = warehouse_id.resource_id.calendar_id
        else:
            calendar_id = self.env.user.company_id.calendar_id
        if not calendar_id:
            calendar_id = self.env.ref("procurement_working_days.default_calendar")
        return calendar_id, resource_id

    def _get_supplier_calendar(self):
        """Returns the applicable (calendar, resource) tuple to use for calculating supplier lead times.
        The applicable calendar is the calendar of the resource defined for this supplier or the module's default
        calendar which considers workings days as being Monday to Friday.
        The applicable resource if the supplier's resource if defined."""
        calendar_id = False
        supplier_id = self._get_product_supplier(self)
        resource_id = supplier_id and supplier_id.resource_id
        if resource_id:
            calendar_id = supplier_id.resource_id.calendar_id
        if not calendar_id:
            calendar_id = self.env.ref("procurement_working_days.default_calendar")
        return calendar_id, resource_id

    @api.model
    def _run_move_create(self, procurement):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'move') set on it.
        Overridden to calculate dates taking into account the applicable working days calendar.

        :param procurement: browse record
        :rtype: dictionary
        '''
        vals = super(procurement_working_days, self)._run_move_create(procurement)
        calendar_id, resource_id = procurement._get_move_calendar()
        proc_date = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        newdate = procurement._schedule_working_days(-procurement.rule_id.delay or 0,
                                                     proc_date,
                                                     resource_id,
                                                     calendar_id)
        vals.update({'date': newdate.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                     'date_expected': newdate.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return vals

    @api.model
    def _get_purchase_schedule_date(self, procurement, company):
        """Return the datetime value to use as Schedule Date (``date_planned``) for the
           Purchase Order Lines created to satisfy the given procurement.
           Overriden here to calculate dates taking into account the applicable working days calendar of our warehouse
           or our company.

           :param browse_record procurement: the procurement for which a PO will be created.
           :param browse_report company: the company to which the new PO will belong to.
           :rtype: datetime
           :return: the desired Schedule Date for the PO lines
        """
        calendar_id, resource_id = procurement._get_move_calendar()
        proc_date = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = procurement._schedule_working_days(-company.po_lead, proc_date, resource_id, calendar_id)
        return schedule_date

    @api.model
    def _get_purchase_order_date(self, procurement, company, schedule_date):
        """Return the datetime value to use as Order Date (``date_order``) for the
           Purchase Order created to satisfy the given procurement.
           Overriden here to calculate dates taking into account the applicable working days calendar.

           :param browse_record procurement: the procurement for which a PO will be created.
           :param browse_report company: the company to which the new PO will belong to.
           :param datetime schedule_date: desired Scheduled Date for the Purchase Order lines.
           :rtype: datetime
           :return: the desired Order Date for the PO
        """
        calendar_id, resource_id = procurement._get_supplier_calendar()
        seller_delay = int(procurement.product_id.seller_delay)
        order_date = procurement._schedule_working_days(-seller_delay, schedule_date, resource_id, calendar_id)
        return order_date

    @api.model
    def _get_date_planned(self, procurement):
        """Returns the planned date for the production.order to be made from this procurement."""
        calendar_id, resource_id = procurement._get_move_calendar()
        format_date_planned = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        date_planned = procurement._schedule_working_days(-procurement.product_id.produce_delay or 0.0,
                                                          format_date_planned,
                                                          resource_id,
                                                          calendar_id)
        date_planned = procurement._schedule_working_days(-procurement.company_id.manufacturing_lead,
                                                          date_planned,
                                                          resource_id,
                                                          calendar_id)
        return date_planned

