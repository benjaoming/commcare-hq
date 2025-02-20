"""
FormES
--------
"""
from django.conf import settings

from corehq.pillows.mappings.const import NULL_VALUE

from . import filters
from .client import ElasticDocumentAdapter, create_document_adapter
from .es_query import HQESQuery
from .index.settings import IndexSettingsKey
from .transient_util import get_adapter_mapping, from_dict_with_possible_id


class FormES(HQESQuery):
    index = 'forms'
    default_filters = {
        'is_xform_instance': filters.term("doc_type", "xforminstance"),
        'has_xmlns': filters.exists("xmlns"),
        'has_user': filters.exists("form.meta.userID"),
        'has_domain': filters.exists("domain"),
    }

    @property
    def builtin_filters(self):
        return [
            form_ids,
            xmlns,
            app,
            submitted,
            completed,
            user_id,
            user_type,
            user_ids_handle_unknown,
            j2me_submissions,
            updating_cases,
        ] + super(FormES, self).builtin_filters

    def user_aggregation(self):
        return self.terms_aggregation('form.meta.userID', 'user')

    def domain_aggregation(self):
        return self.terms_aggregation('domain.exact', 'domain')

    def only_archived(self):
        """Include only archived forms, which are normally excluded"""
        return (self.remove_default_filter('is_xform_instance')
                .filter(filters.doc_type('xformarchived')))


class ElasticForm(ElasticDocumentAdapter):

    settings_key = IndexSettingsKey.FORMS

    @property
    def mapping(self):
        return get_adapter_mapping(self)

    @classmethod
    def from_python(cls, doc):
        return from_dict_with_possible_id(doc)


form_adapter = create_document_adapter(
    ElasticForm,
    getattr(settings, "ES_XFORM_INDEX_NAME", "xforms_2016-07-07"),
    "xform",
)


def form_ids(form_ids):
    return filters.term('_id', form_ids)


def xmlns(xmlnss):
    return filters.term('xmlns.exact', xmlnss)


def app(app_ids):
    return filters.term('app_id', app_ids)


def submitted(gt=None, gte=None, lt=None, lte=None):
    return filters.date_range('received_on', gt, gte, lt, lte)


def completed(gt=None, gte=None, lt=None, lte=None):
    return filters.date_range('form.meta.timeEnd', gt, gte, lt, lte)


def user_id(user_ids):
    if not isinstance(user_ids, (list, set, tuple)):
        user_ids = [user_ids]
    return filters.term(
        'form.meta.userID',
        [x if x is not None else NULL_VALUE for x in user_ids]
    )


def user_type(user_types):
    return filters.term("user_type", user_types)


def user_ids_handle_unknown(user_ids):
    missing_users = None in user_ids

    user_ids = [_f for _f in user_ids if _f]

    if not missing_users:
        user_filter = user_id(user_ids)
    elif user_ids and missing_users:
        user_filter = filters.OR(
            user_id(user_ids),
            filters.missing('form.meta.userID'),
        )
    else:
        user_filter = filters.missing('form.meta.userID')
    return user_filter


def j2me_submissions(gt=None, gte=None, lt=None, lte=None):
    return filters.AND(
        filters.regexp("form.meta.appVersion", "v2+.[0-9]+.*"),
        submitted(gt, gte, lt, lte)
    )


def updating_cases(case_ids):
    """return only those forms that have case blocks that touch the cases listed in `case_ids`
    """
    return filters.term("__retrieved_case_ids", case_ids)
