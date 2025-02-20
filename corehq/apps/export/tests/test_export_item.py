from collections import namedtuple

from django.test import SimpleTestCase

from unittest import mock

from corehq.apps.export.models import (
    ExportColumn,
    ExportItem,
    MultipleChoiceItem,
    Option,
)
from corehq.apps.export.models.new import MAIN_TABLE, PathNode

MockRequest = namedtuple('MockRequest', 'domain')


@mock.patch(
    'corehq.apps.export.models.new.get_request_domain',
    return_value=MockRequest(domain='my-domain'),
)
class TestExportItemGeneration(SimpleTestCase):
    app_id = '1234'

    def setUp(self):
        self.item = ExportItem(
            path=[PathNode(name='data'), PathNode(name='question1')],
            label='Question One',
            last_occurrences={self.app_id: 3},
        )

    def test_create_default_from_export_item(self, _):
        column = ExportColumn.create_default_from_export_item(MAIN_TABLE, self.item, {self.app_id: 3})

        self.assertEqual(column.is_advanced, False)
        self.assertEqual(column.is_deleted, False)
        self.assertEqual(column.is_deprecated, False)
        self.assertEqual(column.label, 'data.question1')
        self.assertEqual(column.selected, True)

    def test_create_default_from_export_item_deleted(self, _):
        column = ExportColumn.create_default_from_export_item(MAIN_TABLE, self.item, {self.app_id: 4})

        self.assertEqual(column.is_advanced, False)
        self.assertEqual(column.is_deleted, True)
        self.assertEqual(column.is_deprecated, False)
        self.assertEqual(column.label, 'data.question1')
        self.assertEqual(column.selected, False)

    def test_create_default_from_export_item_deprecated(self, _):
        column = ExportColumn.create_default_from_export_item(
            table_path=MAIN_TABLE,
            item=self.item,
            app_ids_and_versions={self.app_id: 3},
            is_deprecated=True
        )

        self.assertEqual(column.is_advanced, False)
        self.assertEqual(column.is_deleted, False)
        self.assertEqual(column.is_deprecated, True)
        self.assertEqual(column.label, 'data.question1')
        self.assertEqual(column.selected, False)

    def test_create_default_from_export_item_not_main_table(self, _):
        column = ExportColumn.create_default_from_export_item(['other_table'], self.item, {self.app_id: 3})

        self.assertEqual(column.is_advanced, False)
        self.assertEqual(column.is_deleted, False)
        self.assertEqual(column.is_deprecated, False)
        self.assertEqual(column.label, 'data.question1')
        self.assertEqual(column.selected, False)

    def test_wrap_export_item(self, _):
        path = [PathNode(name="foo"), PathNode(name="bar")]
        item = ExportItem(path=path)
        wrapped = ExportItem.wrap(item.to_json())
        self.assertEqual(type(wrapped), type(item))
        self.assertEqual(wrapped.to_json(), item.to_json())

    def test_wrap_export_item_child(self, _):
        path = [PathNode(name="foo"), PathNode(name="bar")]
        item = MultipleChoiceItem(path=path, options=[Option(value="foo")])
        wrapped = ExportItem.wrap(item.to_json())
        self.assertEqual(type(wrapped), type(item))
        self.assertEqual(wrapped.to_json(), item.to_json())


class CreateFromQuestionTests(SimpleTestCase):
    def test_removes_html_from_label(self):
        question = {
            'label': '<span style="color:#ffffff">Enter a number</span>',
            'value': '/data/enter_number',
            'type': 'Int',
        }

        item = ExportItem.create_from_question(question, 'app_id', 'app_ersion', [])
        self.assertEqual(item.label, 'Enter a number')
