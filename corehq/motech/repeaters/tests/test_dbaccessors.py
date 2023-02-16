import uuid
from datetime import datetime, timedelta

from django.test import TestCase

from corehq.motech.repeaters.const import RECORD_PENDING_STATE
from corehq.motech.repeaters.dbaccessors import (
    get_domains_that_have_repeat_records,
    get_failure_repeat_record_count,
    get_overdue_repeat_record_count,
    get_paged_repeat_records,
    get_pending_repeat_record_count,
    get_repeat_record_count,
    get_repeat_records_by_payload_id,
    get_success_repeat_record_count,
    iter_repeat_records_by_domain,
    iterate_repeat_record_ids,
    get_paged_sql_repeat_records,
)
from corehq.motech.repeaters.models import RepeatRecord, SQLRepeatRecordAttempt
from dimagi.utils.dates import DateSpan
from .test_models import RepeaterTestCase


class TestRepeatRecordDBAccessors(TestCase):
    repeater_id = '1234'
    other_id = '5678'
    domain = 'test-domain-2'

    @classmethod
    def setUpClass(cls):
        super(TestRepeatRecordDBAccessors, cls).setUpClass()
        before = datetime.utcnow() - timedelta(minutes=5)
        cls.payload_id_1 = uuid.uuid4().hex
        cls.payload_id_2 = uuid.uuid4().hex
        failed = RepeatRecord(
            domain=cls.domain,
            failure_reason='Some python error',
            repeater_id=cls.repeater_id,
            next_check=before,
            payload_id=cls.payload_id_1,
        )
        failed_hq_error = RepeatRecord(
            domain=cls.domain,
            failure_reason='Some python error',
            repeater_id=cls.repeater_id,
            next_check=before,
            payload_id=cls.payload_id_1,
        )
        failed_hq_error.doc_type += '-Failed'
        success = RepeatRecord(
            domain=cls.domain,
            succeeded=True,
            repeater_id=cls.repeater_id,
            next_check=before,
            payload_id=cls.payload_id_2,
        )
        pending = RepeatRecord(
            domain=cls.domain,
            succeeded=False,
            repeater_id=cls.repeater_id,
            next_check=before,
            payload_id=cls.payload_id_2,
        )
        overdue = RepeatRecord(
            domain=cls.domain,
            succeeded=False,
            repeater_id=cls.repeater_id,
            next_check=before - timedelta(minutes=10),
            payload_id=cls.payload_id_2,
        )
        other_id = RepeatRecord(
            domain=cls.domain,
            succeeded=False,
            repeater_id=cls.other_id,
            next_check=before,
            payload_id=cls.payload_id_2,
        )

        cls.records = [
            failed,
            failed_hq_error,
            success,
            pending,
            overdue,
            other_id,
        ]

        for record in cls.records:
            record.save()

    @classmethod
    def tearDownClass(cls):
        for record in cls.records:
            record.delete()
        super(TestRepeatRecordDBAccessors, cls).tearDownClass()

    def test_get_pending_repeat_record_count(self):
        count = get_pending_repeat_record_count(self.domain, self.repeater_id)
        self.assertEqual(count, 2)

    def test_get_success_repeat_record_count(self):
        count = get_success_repeat_record_count(self.domain, self.repeater_id)
        self.assertEqual(count, 1)

    def test_get_failure_repeat_record_count(self):
        count = get_failure_repeat_record_count(self.domain, self.repeater_id)
        self.assertEqual(count, 2)

    def test_get_repeat_record_count_with_state_and_no_repeater(self):
        count = get_repeat_record_count(self.domain, state=RECORD_PENDING_STATE)
        self.assertEqual(count, 3)

    def test_get_repeat_record_count_with_repeater_id_and_no_state(self):
        count = get_repeat_record_count(self.domain, repeater_id=self.other_id)
        self.assertEqual(count, 1)

    def test_get_paged_repeat_records_with_state_and_no_records(self):
        count = get_repeat_record_count('wrong-domain', state=RECORD_PENDING_STATE)
        self.assertEqual(count, 0)

    def test_get_paged_repeat_records(self):
        records = get_paged_repeat_records(self.domain, 0, 2)
        self.assertEqual(len(records), 2)

    def test_get_paged_repeat_records_with_repeater_id(self):
        records = get_paged_repeat_records(self.domain, 0, 2, repeater_id=self.other_id)
        self.assertEqual(len(records), 1)

    def test_get_paged_repeat_records_with_state(self):
        records = get_paged_repeat_records(self.domain, 0, 10, state=RECORD_PENDING_STATE)
        self.assertEqual(len(records), 3)

    def test_get_paged_repeat_records_wrong_domain(self):
        records = get_paged_repeat_records('wrong-domain', 0, 2)
        self.assertEqual(len(records), 0)

    def test_get_all_paged_repeat_records(self):
        records = get_paged_repeat_records(self.domain, 0, 10)
        self.assertEqual(len(records), len(self.records))  # get all the records that were created

    def test_iterate_repeat_records(self):
        records = list(iterate_repeat_record_ids(datetime.utcnow(), chunk_size=2))
        self.assertEqual(len(records), 4)  # Should grab all but the succeeded one

    def test_get_overdue_repeat_record_count(self):
        overdue_count = get_overdue_repeat_record_count()
        self.assertEqual(overdue_count, 1)

    def test_get_paged_repeat_records_by_last_checked(self):
        today = datetime.utcnow()
        specific_id = 'some_id'

        def _record(last_checked):
            return RepeatRecord(
                domain=self.domain,
                last_checked=last_checked,
                succeeded=False,
                repeater_id=self.other_id,
                next_check=today,
                payload_id=self.payload_id_2,
            )

        two_days_ago = RepeatRecord(
            domain=self.domain,
            last_checked=today - timedelta(days=2),
            succeeded=False,
            failure_reason='some error',
            repeater_id=specific_id,
            next_check=today,
            payload_id=self.payload_id_2,
        )
        on_today = RepeatRecord(
            domain=self.domain,
            last_checked=today + timedelta(days=2),
            succeeded=True,
            repeater_id=self.other_id,
            next_check=today,
            payload_id=self.payload_id_2,
        )
        two_days_latter = RepeatRecord(
            domain=self.domain,
            last_checked=today,
            succeeded=False,
            repeater_id=specific_id,
            next_check=today,
            payload_id=self.payload_id_2,
        )
        records = [two_days_ago, on_today, two_days_latter]
        RepeatRecord.bulk_save(records)

        def _get_records(startdate, enddate, state=None, repeater_id=None):
            return get_paged_repeat_records(
                self.domain, 0, 10,
                datespan=DateSpan(startdate, enddate),
                state=state,
                repeater_id=repeater_id,
            )

        # Test only by last_checked
        self.assertEqual(
            len(_get_records(today - timedelta(days=3), today + timedelta(days=3))),
            3
        )
        self.assertEqual(
            len(_get_records(today - timedelta(days=1), today + timedelta(days=1))),
            1
        )
        # Test state as well
        self.assertEqual(
            len(_get_records(today - timedelta(days=3), today + timedelta(days=3), state='FAIL')),
            1
        )
        # Test repeater_id as well
        self.assertEqual(
            len(_get_records(today - timedelta(days=0), today + timedelta(days=2), repeater_id=specific_id)),
            1
        )
        # Test state and repeater_id
        self.assertEqual(
            len(_get_records(today - timedelta(days=3),
                today + timedelta(days=3), state='FAIL', repeater_id=specific_id)),
            1
        )
        RepeatRecord.bulk_delete(records)

    def test_get_all_repeat_records_by_domain_wrong_domain(self):
        records = list(iter_repeat_records_by_domain("wrong-domain"))
        self.assertEqual(len(records), 0)

    def test_get_all_repeat_records_by_domain_with_repeater_id(self):
        records = list(iter_repeat_records_by_domain(self.domain, repeater_id=self.repeater_id))
        self.assertEqual(len(records), 5)

    def test_get_all_repeat_records_by_domain(self):
        records = list(iter_repeat_records_by_domain(self.domain))
        self.assertEqual(len(records), len(self.records))

    def test_get_repeat_records_by_payload_id(self):
        id_1_records = list(get_repeat_records_by_payload_id(self.domain, self.payload_id_1))
        self.assertEqual(len(id_1_records), 2)
        self.assertItemsEqual([r._id for r in id_1_records], [r._id for r in self.records[0:2]])

        id_2_records = list(get_repeat_records_by_payload_id(self.domain, self.payload_id_2))
        self.assertEqual(len(id_2_records), 4)
        self.assertItemsEqual([r._id for r in id_2_records], [r._id for r in self.records[2:6]])


class TestOtherDBAccessors(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestOtherDBAccessors, cls).setUpClass()
        cls.records = [
            RepeatRecord(domain='a'),
            RepeatRecord(domain='b'),
            RepeatRecord(domain='c'),
        ]
        RepeatRecord.bulk_save(cls.records)

    @classmethod
    def tearDownClass(cls):
        RepeatRecord.bulk_delete(cls.records)
        super(TestOtherDBAccessors, cls).tearDownClass()

    def test_get_domains_that_have_repeat_records(self):
        self.assertEqual(get_domains_that_have_repeat_records(), ['a', 'b', 'c'])


class TestSQLDBAccessors(RepeaterTestCase):

    def test_get_paged_sql_repeat_records_daterange(self):
        domain = 'test-sql'
        eve = self.repeater.repeat_records.create(
            domain=domain,
            payload_id='eve',
            registered_at='1970-02-01',
        )
        moon = self.repeater.repeat_records.create(
            domain=domain,
            payload_id='moon',
            registered_at='1970-02-01',
        )
        eve_old = SQLRepeatRecordAttempt.objects.create(
            repeat_record=eve,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        moon_new = SQLRepeatRecordAttempt.objects.create(
            repeat_record=moon,
            created_at=datetime.utcnow() + timedelta(days=2)
        )
        self.assertQuerysetEqual(
            get_paged_sql_repeat_records(domain, 0, 10),
            [eve, moon],
            ordered=False
        )
        self.assertQuerysetEqual(
            get_paged_sql_repeat_records(domain, 0, 10,
                datespan=DateSpan(datetime.utcnow() - timedelta(days=3), datetime.utcnow() + timedelta(days=3))),
            [eve, moon],
            ordered=False
        )
        self.assertQuerysetEqual(
            get_paged_sql_repeat_records(domain, 0, 10,
                datespan=DateSpan(datetime.utcnow() - timedelta(days=3), datetime.utcnow() + timedelta(days=1))),
            [eve]
        )
        self.assertQuerysetEqual(
            get_paged_sql_repeat_records(domain, 0, 10,
                datespan=DateSpan(datetime.utcnow() - timedelta(days=1), datetime.utcnow() + timedelta(days=3))),
            [moon]
        )
        for obj in [eve, moon, eve_old, moon_new]:
            obj.delete()
