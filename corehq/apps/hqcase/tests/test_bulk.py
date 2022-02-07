import uuid
from unittest import mock

from django.test import TestCase

from casexml.apps.case.mock import CaseBlock

from corehq.apps.hqcase.bulk import CaseBulkDB, update_cases
from corehq.form_processor.interfaces.dbaccessors import CaseAccessors
from corehq.form_processor.models import XFormInstance
from corehq.form_processor.tests.utils import FormProcessorTestUtils


@mock.patch('corehq.apps.hqcase.bulk.CASEBLOCK_CHUNKSIZE', new=5)
class TestUpdateCases(TestCase):
    domain = 'test_bulk_update_cases'

    def tearDown(self):
        FormProcessorTestUtils.delete_all_xforms()
        FormProcessorTestUtils.delete_all_cases()
        super().tearDown()

    def test(self):
        case_accessor = CaseAccessors(self.domain)
        case_ids = [str(uuid.uuid4()) for i in range(1, 18)]

        with CaseBulkDB(self.domain, 'my_user_id', 'my_device_id') as bulk_db:
            for i, case_id in enumerate(case_ids):
                bulk_db.save(CaseBlock(
                    create=True,
                    case_id=case_id,
                    case_type='patient',
                    case_name=f"case_{i}",
                    update={
                        'phase': '1',
                        'to_update': 'yes' if i % 2 else 'no',
                    },
                ))

        self.assertEqual(len(XFormInstance.objects.get_form_ids_in_domain(self.domain)), 4)
        self.assertEqual(len(case_accessor.get_case_ids_in_domain()), len(case_ids))

        update_cases(self.domain, _set_phase_2, case_ids, 'my_user_id', 'my_device_id')

        for case in case_accessor.get_cases(case_ids):
            correct_phase = '2' if case.get_case_property('to_update') == 'yes' else '1'
            self.assertEqual(case.get_case_property('phase'), correct_phase)


def _set_phase_2(case):
    if case.get_case_property('to_update') == 'yes':
        return CaseBlock(
            case_id=case.case_id,
            update={'phase': '2'},
        )
