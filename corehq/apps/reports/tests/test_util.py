import os
from unittest.mock import patch, Mock

from django.core.cache import cache
from django.test import SimpleTestCase

from testil import eq

from corehq.apps.reports.tasks import summarize_user_counts
from corehq.apps.reports.util import get_user_id_from_form
from corehq.form_processor.exceptions import XFormNotFound
from corehq.form_processor.models import XFormInstance
from corehq.form_processor.utils import TestFormMetadata
from corehq.util.test_utils import TestFileMixin, get_form_ready_to_save
from corehq.apps.reports.standard.cases.utils import get_user_type

DOMAIN = 'test_domain'
USER_ID = "5bc1315c-da6f-466d-a7c4-4580bc84a7b9"


class TestSummarizeUserCounts(SimpleTestCase):
    def test_summarize_user_counts(self):
        self.assertEqual(
            summarize_user_counts({'a': 1, 'b': 10, 'c': 2}, n=0),
            {(): 13},
        )
        self.assertEqual(
            summarize_user_counts({'a': 1, 'b': 10, 'c': 2}, n=1),
            {'b': 10, (): 3},
        )
        self.assertEqual(
            summarize_user_counts({'a': 1, 'b': 10, 'c': 2}, n=2),
            {'b': 10, 'c': 2, (): 1},
        )
        self.assertEqual(
            summarize_user_counts({'a': 1, 'b': 10, 'c': 2}, n=3),
            {'a': 1, 'b': 10, 'c': 2, (): 0},
        )
        self.assertEqual(
            summarize_user_counts({'a': 1, 'b': 10, 'c': 2}, n=4),
            {'a': 1, 'b': 10, 'c': 2, (): 0},
        )


class TestGetUserType(SimpleTestCase):
    def setUp(self):
        self.form_metadata = Mock(userID=None, username='foobar')

    def test_unknown_user(self):
        self.assertEqual(get_user_type(self.form_metadata), 'Unknown')

    def test_system_user(self):
        self.form_metadata.username = 'system'
        self.assertEqual(get_user_type(self.form_metadata), 'System')

    @patch(
        'corehq.apps.reports.standard.cases.utils.get_doc_info_by_id',
        return_value=Mock(type_display='Foobar')
    )
    def test_display_user(self, _):
        self.form_metadata.userID = '1234'
        self.assertEqual(get_user_type(self.form_metadata), 'Foobar')


def test_get_user_id():
    form_id = "acca290f-22fc-4c5c-8cce-ee253ca5678b"
    reset_cache(form_id)
    with patch.object(XFormInstance.objects, "get_form", get_form):
        eq(get_user_id_from_form(form_id), USER_ID)


def test_get_user_id_cached():
    form_id = "d1667406-319f-4d0c-9091-0d6c0032363a"
    reset_cache(form_id, USER_ID)
    with patch.object(XFormInstance.objects, "get_form", form_not_found):
        eq(get_user_id_from_form(form_id), USER_ID)


def test_get_user_id_not_found():
    form_id = "73bfc6a5-c66e-4b17-be6d-45513511e1ef"
    reset_cache(form_id)
    with patch.object(XFormInstance.objects, "get_form", form_not_found):
        eq(get_user_id_from_form(form_id), None)

    with patch.object(XFormInstance.objects, "get_form", get_form):
        # null value should not be cached
        eq(get_user_id_from_form(form_id), USER_ID)


def get_form(form_id):
    metadata = TestFormMetadata(domain="test", user_id=USER_ID)
    return get_form_ready_to_save(metadata, form_id=form_id)


def form_not_found(form_id):
    raise XFormNotFound(form_id)


def reset_cache(form_id, value=None):
    key = f'xform-{form_id}-user_id'
    if value is None:
        cache.delete(key)
    else:
        cache.set(key, value, 5)
