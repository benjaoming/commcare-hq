import uuid

from django.test import TestCase

from pillowtop.es_utils import initialize_index_and_mapping

from corehq.apps.domain.shortcuts import create_domain
from corehq.apps.es.tests.utils import es_test
from corehq.apps.locations.models import LocationType, SQLLocation
from corehq.apps.userreports.app_manager.helpers import clean_table_name
from corehq.apps.userreports.models import DataSourceConfiguration
from corehq.apps.userreports.pillow import get_location_pillow
from corehq.apps.userreports.tasks import rebuild_indicators
from corehq.apps.userreports.util import get_indicator_adapter
from corehq.elastic import get_es_new
from corehq.pillows.mappings.user_mapping import USER_INDEX_INFO
from corehq.util.elastic import ensure_index_deleted


@es_test
class TestLocationDataSource(TestCase):
    domain = "delos_corp"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.domain_obj = create_domain(cls.domain)
        cls.addClassCleanup(cls.domain_obj.delete)

    def setUp(self):
        super().setUp()
        es = get_es_new()
        initialize_index_and_mapping(es, USER_INDEX_INFO)
        self.addCleanup(ensure_index_deleted, USER_INDEX_INFO.index)
        self.region = LocationType.objects.create(domain=self.domain, name="region")
        self.town = LocationType.objects.create(domain=self.domain, name="town", parent_type=self.region)

        self.data_source_config = DataSourceConfiguration(
            domain=self.domain,
            display_name='Locations in Westworld',
            referenced_doc_type='Location',
            table_id=clean_table_name(self.domain, str(uuid.uuid4().hex)),
            configured_filter={},
            configured_indicators=[{
                "type": "expression",
                "expression": {
                    "type": "property_name",
                    "property_name": "name"
                },
                "column_id": "location_name",
                "display_name": "location_name",
                "datatype": "string"
            }],
        )
        self.data_source_config.validate()
        self.data_source_config.save()
        self.addCleanup(self.data_source_config.delete)

        adapter = get_indicator_adapter(self.data_source_config)
        self.addCleanup(adapter.drop_table)

        self.pillow = get_location_pillow(ucr_configs=[self.data_source_config])
        self.pillow.get_change_feed().get_latest_offsets()

    def _make_loc(self, name, location_type):
        return SQLLocation.objects.create(
            domain=self.domain, name=name, site_code=name, location_type=location_type)

    def assertDataSourceAccurate(self, expected_locations):
        adapter = get_indicator_adapter(self.data_source_config)
        query = adapter.get_query_object()
        data_source = query.all()
        self.assertItemsEqual(
            expected_locations,
            [row[-1] for row in data_source]
        )

    def test_location_data_source(self):
        self._make_loc("Westworld", self.region)
        sweetwater = self._make_loc("Sweetwater", self.town)
        las_mudas = self._make_loc("Las Mudas", self.town)

        rebuild_indicators(self.data_source_config._id)

        self.assertDataSourceAccurate(["Westworld", "Sweetwater", "Las Mudas"])

        # Insert new location
        since = self.pillow.get_change_feed().get_latest_offsets()
        self._make_loc("Blood Arroyo", self.town)

        # Change an existing location
        sweetwater.name = "Pariah"
        sweetwater.save()

        # Process both changes together and verify that they went through
        self.pillow.process_changes(since=since, forever=False)
        self.assertDataSourceAccurate(["Westworld", "Pariah", "Las Mudas", "Blood Arroyo"])

        # Delete a location
        since = self.pillow.get_change_feed().get_latest_offsets()
        las_mudas.delete()
        self.pillow.process_changes(since=since, forever=False)
        self.assertDataSourceAccurate(["Westworld", "Pariah", "Blood Arroyo"])
