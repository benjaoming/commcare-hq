from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from corehq.apps.reports.datatables import DataTablesColumn, DataTablesHeader
from corehq.apps.reports.dispatcher import DomainReportDispatcher
from corehq.apps.reports.filters.base import BaseMultipleOptionFilter
from corehq.apps.reports.generic import GenericTabularReport
from corehq.apps.reports.standard import DatespanMixin
from corehq.toggles import GENERIC_INBOUND_API

from .models import RequestLog


class RequestStatusFilter(BaseMultipleOptionFilter):
    slug = 'request_status'
    label = gettext_lazy('Request Status')

    @property
    def options(self):
        return RequestLog.Status.choices


class ApiRequestLogReport(DatespanMixin, GenericTabularReport):
    name = gettext_lazy('Inbound API Request Logs')
    slug = 'api_request_log_report'
    base_template = "reports/base_template.html"
    section_name = gettext_lazy('Project Settings')
    dispatcher = DomainReportDispatcher
    ajax_pagination = True
    sortable = False

    fields = [
        'corehq.apps.reports.filters.dates.DatespanFilter',
        'corehq.motech.generic_inbound.reports.RequestStatusFilter',
    ]

    toggles = [GENERIC_INBOUND_API]

    @classmethod
    def allow_access(cls, request):
        return request.couch_user.is_domain_admin()

    @property
    def total_records(self):
        return self._queryset.count()

    @property
    def shared_pagination_GET_params(self):
        return [
            {'name': param, 'value': self.request.GET.getlist(param)}
            for param in ['request_status', 'startdate', 'enddate']
        ]

    @property
    def headers(self):
        return DataTablesHeader(
            DataTablesColumn(_("API")),
            DataTablesColumn(_("Timestamp")),
            DataTablesColumn(_("Status")),
            DataTablesColumn(_("Response")),
        )

    @cached_property
    def _queryset(self):
        queryset = RequestLog.objects.filter(
            domain=self.domain,
            timestamp__gte=self.request.datespan.startdate_utc,
            timestamp__lt=self.request.datespan.enddate_utc,
        )
        status = self.request.GET.getlist('request_status')
        if status:
            queryset = queryset.filter(status__in=status)
        return queryset

    @property
    def rows(self):
        status_labels = dict(RequestLog.Status.choices)
        for log in self._queryset[self.pagination.start:self.pagination.end]:
            yield [
                log.api.name,
                log.timestamp,
                status_labels[log.status],
                log.response_status,
            ]
