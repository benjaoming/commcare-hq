from __future__ import absolute_import
from django.utils.translation import ugettext_lazy as _
from corehq.apps.change_feed.topics import CASE, CASE_SQL, FORM, FORM_SQL, LOCATION

REPORT_BUILDER_EVENTS_KEY = 'REPORT_BUILDER_EVENTS_KEY'

DATA_SOURCE_NOT_FOUND_ERROR_MESSAGE = _(
    'Sorry! There was a problem viewing your report. '
    'This likely occurred because the application associated with the report was deleted. '
    'In order to view this data using the Report Builder you will have to delete this report '
    'and then build it again. Click below to delete it.'
)

UCR_SQL_BACKEND = "SQL"
UCR_ES_BACKEND = "ES"
UCR_LABORATORY_BACKEND = "LABORATORY"

UCR_BACKENDS = [UCR_SQL_BACKEND, UCR_ES_BACKEND]

DEFAULT_MAXIMUM_EXPANSION = 10

UCR_CELERY_QUEUE = 'ucr_queue'

KAFKA_TOPICS = (
    CASE,
    CASE_SQL,
    FORM,
    FORM_SQL,
    LOCATION,
)
