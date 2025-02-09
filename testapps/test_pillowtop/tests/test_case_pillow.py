import uuid
from unittest.mock import patch

from django.test import TestCase

from pillow_retry.models import PillowError
from pillowtop.es_utils import initialize_index_and_mapping

from corehq.apps.case_search.models import CaseSearchConfig
from corehq.apps.es import CaseES, CaseSearchES
from corehq.apps.es.tests.utils import es_test
from corehq.elastic import get_es_new
from corehq.form_processor.models import CommCareCase
from corehq.form_processor.tests.utils import FormProcessorTestUtils, create_case
from corehq.pillows.case_search import domains_needing_search_index
from corehq.pillows.mappings.case_mapping import CASE_INDEX_INFO
from corehq.pillows.mappings.case_search_mapping import CASE_SEARCH_INDEX_INFO
from corehq.util.elastic import ensure_index_deleted
from corehq.util.es.elasticsearch import ConnectionError
from corehq.util.test_utils import trap_extra_setup
from testapps.test_pillowtop.utils import process_pillow_changes


@es_test
class CasePillowTest(TestCase):
    domain = 'case-pillowtest-domain'

    @classmethod
    def setUpClass(cls):
        super(CasePillowTest, cls).setUpClass()
        ensure_index_deleted(CASE_INDEX_INFO.index)
        ensure_index_deleted(CASE_SEARCH_INDEX_INFO.index)
        # enable case search for this domain
        CaseSearchConfig.objects.create(domain=cls.domain, enabled=True)
        domains_needing_search_index.clear()

    def setUp(self):
        super(CasePillowTest, self).setUp()
        self.process_case_changes = process_pillow_changes('DefaultChangeFeedPillow')
        self.process_case_changes.add_pillow('case-pillow', {'skip_ucr': True})
        FormProcessorTestUtils.delete_all_cases()
        with trap_extra_setup(ConnectionError):
            self.elasticsearch = get_es_new()
            initialize_index_and_mapping(self.elasticsearch, CASE_INDEX_INFO)
            initialize_index_and_mapping(self.elasticsearch, CASE_SEARCH_INDEX_INFO)

    def tearDown(self):
        ensure_index_deleted(CASE_INDEX_INFO.index)
        ensure_index_deleted(CASE_SEARCH_INDEX_INFO.index)
        FormProcessorTestUtils.delete_all_cases_forms_ledgers(self.domain)
        PillowError.objects.all().delete()
        super(CasePillowTest, self).tearDown()

    def test_case_pillow(self):
        case_id, case_name = self._create_case_and_sync_to_es()

        # confirm change made it to elasticserach
        results = CaseES().run()
        self.assertEqual(1, results.total)
        case_doc = results.hits[0]
        self.assertEqual(self.domain, case_doc['domain'])
        self.assertEqual(case_id, case_doc['_id'])
        self.assertEqual(case_name, case_doc['name'])

    def test_case_pillow_error_in_case_es(self):
        self.assertEqual(0, PillowError.objects.filter(pillow='case-pillow').count())
        with patch('corehq.pillows.case_search.domain_needs_search_index', return_value=True), \
            patch('corehq.pillows.case.transform_case_for_elasticsearch') as case_transform, \
            patch('corehq.pillows.case_search.transform_case_for_elasticsearch') as case_search_transform:
                case_transform.side_effect = Exception('case_transform error')
                case_search_transform.side_effect = Exception('case_search_transform error')
                case_id, case_name = self._create_case_and_sync_to_es()

        # confirm change did not make it to case search index
        results = CaseSearchES().run()
        self.assertEqual(0, results.total)

        # confirm change did not make it to case index
        results = CaseES().run()
        self.assertEqual(0, results.total)

        self.assertEqual(1, PillowError.objects.filter(pillow='case-pillow').count())

    def test_case_soft_deletion(self):
        case_id, case_name = self._create_case_and_sync_to_es()

        # verify there
        results = CaseES().run()
        self.assertEqual(1, results.total)
        search_results = CaseSearchES().run()
        self.assertEqual(1, search_results.total)

        # soft delete the case
        with self.process_case_changes:
            CommCareCase.objects.soft_delete_cases(self.domain, [case_id])
        self.elasticsearch.indices.refresh(CASE_INDEX_INFO.index)
        self.elasticsearch.indices.refresh(CASE_SEARCH_INDEX_INFO.index)

        # ensure not there anymore
        results = CaseES().run()
        self.assertEqual(0, results.total)
        search_results = CaseSearchES().run()
        self.assertEqual(0, search_results.total)

    def test_case_hard_deletion(self):
        case_id, case_name = self._create_case_and_sync_to_es()

        # verify there
        results = CaseES().run()
        self.assertEqual(1, results.total)
        search_results = CaseSearchES().run()
        self.assertEqual(1, search_results.total)

        # hard delete the case
        with self.process_case_changes:
            CommCareCase.objects.hard_delete_cases(self.domain, [case_id])
        self.elasticsearch.indices.refresh(CASE_INDEX_INFO.index)
        self.elasticsearch.indices.refresh(CASE_SEARCH_INDEX_INFO.index)

        # ensure not there anymore
        results = CaseES().run()
        self.assertEqual(0, results.total)
        search_results = CaseSearchES().run()
        self.assertEqual(0, search_results.total)

    def _create_case_and_sync_to_es(self):
        case_id = uuid.uuid4().hex
        case_name = 'case-name-{}'.format(uuid.uuid4().hex)
        with self.process_case_changes:
            create_case(self.domain, case_id=case_id, name=case_name, save=True, enable_kafka=True)
        self.elasticsearch.indices.refresh(CASE_INDEX_INFO.index)
        self.elasticsearch.indices.refresh(CASE_SEARCH_INDEX_INFO.index)
        return case_id, case_name
