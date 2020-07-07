from django.test import TestCase

from corehq.apps.custom_data_fields.models import (
    CustomDataFieldsDefinition,
    CustomDataFieldsProfile,
    Field,
)
from corehq.apps.users.views.mobile.custom_data_fields import UserFieldsView


class TestCustomDataFieldsProfile(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.definition = CustomDataFieldsDefinition(domain='a-domain', field_type=UserFieldsView.field_type)
        cls.definition.save()
        cls.definition.set_fields([
            Field(
                slug='corners',
                is_required=True,
                label='Number of corners',
                regex='^[0-9]+$',
                regex_msg='This should be a number',
            ),
            Field(
                slug='prefix',
                is_required=False,
                label='Prefix',
                choices=['tri', 'tetra', 'penta'],
            ),
            Field(
                slug='color',
                is_required=False,
                label='Color',
            ),
        ])
        cls.definition.save()

        cls.profile3 = CustomDataFieldsProfile(
            name='three',
            fields={'corners': 3, 'prefix': 'tri'},
            definition=cls.definition,
        )
        cls.profile3.save()

        cls.profile5 = CustomDataFieldsProfile(
            name='five',
            fields={'corners': 5, 'prefix': 'penta'},
            definition=cls.definition,
        )
        cls.profile5.save()

    @classmethod
    def tearDownClass(cls):
        cls.definition.delete()
        super().tearDownClass()

    def test_to_json(self):
        data = self.profile3.to_json()
        self.assertEqual(data, {
            "id": self.profile3.id,
            "name": "three",
            "fields": {
                "corners": 3,
                "prefix": "tri",
            },
        })

    def test_get_profiles(self):
        profiles = [p.to_json() for p in self.definition.get_profiles()]
        self.assertEqual(profiles, [{
            "id": self.profile5.id,
            "name": "five",
            "fields": {
                "corners": 5,
                "prefix": "penta",
            },
        }, {
            "id": self.profile3.id,
            "name": "three",
            "fields": {
                "corners": 3,
                "prefix": "tri",
            },
        }])
