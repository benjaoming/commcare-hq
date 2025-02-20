from django.conf import settings
from django.test import SimpleTestCase
from corehq.apps.es.tests.utils import es_test
from corehq.pillows.utils import get_all_expected_es_indices


@es_test
class ProdIndexManagementTest(SimpleTestCase):

    maxDiff = None  # show the entire diff for test failures

    @classmethod
    def setUpClass(cls):
        super(ProdIndexManagementTest, cls).setUpClass()
        cls._PILLOWTOPS = settings.PILLOWTOPS
        if not settings.PILLOWTOPS:
            # assumes HqTestSuiteRunner, which blanks this out and saves a copy here
            settings.PILLOWTOPS = settings._PILLOWTOPS

    @classmethod
    def tearDownClass(cls):
        settings.PILLOWTOPS = cls._PILLOWTOPS
        super(ProdIndexManagementTest, cls).tearDownClass()

    def test_prod_config(self):
        # TODO: implement index verification in a way that is reindex-friendly
        found_prod_indices = []
        for index_info in get_all_expected_es_indices():
            if index_info.alias == "pillowtop_tests":
                continue  # skip this one
            info = index_info.to_json()
            found_prod_indices.append(info)
            # for now don"t test this property, just ensure it exist
            self.assertTrue(info["mapping"])
            del info["mapping"]
            # TODO: test mappings.  Seems related, but different from
            # `corehq/pillows/mappings/tests`. The tests here in this module
            # should probably move over there some day.

        def alias(info):
            return info["alias"]

        found_prod_indices = sorted(found_prod_indices, key=alias)
        expected_prod_indices = sorted(EXPECTED_PROD_INDICES, key=alias)
        # compare aliases to make it easier to spot the difference
        # when an index is added or removed
        self.assertEqual(
            [alias(info) for info in expected_prod_indices],
            [alias(info) for info in found_prod_indices],
        )
        # do full comparison once we know the index aliases are the same
        self.assertEqual(expected_prod_indices, found_prod_indices)


EXPECTED_PROD_INDICES = [
    {
        "index": "test_case_search_2018-05-29",
        "alias": "test_case_search",
        "type": "case",
        "hq_index_name": "case_search",
        "meta": {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": [
                                "lowercase"
                            ]
                        },
                        "phonetic": {
                            "filter": [
                                "standard",
                                "lowercase",
                                "soundex"
                            ],
                            "tokenizer": "standard"
                        }
                    },
                    "filter": {
                        "soundex": {
                            "replace": "true",
                            "type": "phonetic",
                            "encoder": "soundex"
                        }
                    }
                },
                "number_of_replicas": 1,
                "number_of_shards": 5,
            }
        }
    },
    {
        "alias": "test_hqapps",
        "hq_index_name": "hqapps",
        "index": "test_hqapps_2020-02-26",
        "type": "app",
        "meta": {
            "settings": {
                "number_of_replicas": 0,
                "number_of_shards": 5,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": ["lowercase"]
                        },
                    }
                }
            }
        }
    },
    {
        "alias": "test_hqcases",
        "hq_index_name": "hqcases",
        "index": "test_hqcases_2016-03-04",
        "type": "case",
        "meta": {
            "settings": {
                "number_of_replicas": 0,
                "number_of_shards": 5,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "filter": [
                                "lowercase"
                            ],
                            "type": "custom",
                            "tokenizer": "whitespace"
                        }
                    }
                }
            }
        }
    },
    {
        "alias": "test_hqdomains",
        "hq_index_name": "hqdomains",
        "index": "test_hqdomains_2021-03-08",
        "type": "hqdomain",
        "meta": {
            "settings": {
                "number_of_replicas": 0,
                "number_of_shards": 5,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": ["lowercase"]
                        },
                        "comma": {
                            "type": "pattern",
                            "pattern": r"\s*,\s*"
                        },
                    }
                }
            }
        }
    },
    {
        "alias": "test_hqgroups",
        "hq_index_name": "hqgroups",
        "index": "test_hqgroups_2017-05-29",
        "type": "group",
        "meta": {
            "settings": {
                "number_of_replicas": 0,
                "number_of_shards": 5,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "filter": [
                                "lowercase"
                            ],
                            "type": "custom",
                            "tokenizer": "whitespace"
                        }
                    }
                }
            }
        }
    },
    {
        "alias": "test_hqusers",
        "hq_index_name": "hqusers",
        "index": "test_hqusers_2017-09-07",
        "type": "user",
        "meta": {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": ["lowercase"]
                        },
                    }
                }
            }
        }
    },
    {
        "alias": "test_smslogs",
        "hq_index_name": "smslogs",
        "index": "test_smslogs_2020-01-28",
        "type": "sms",
        "meta": {
            "settings": {
                "number_of_replicas": 0,
                "number_of_shards": 5,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "filter": [
                                "lowercase"
                            ],
                            "type": "custom",
                            "tokenizer": "whitespace"
                        }
                    }
                }
            }
        }
    },
    {
        "alias": "test_xforms",
        "hq_index_name": "xforms",
        "index": "test_xforms_2016-07-07",
        "type": "xform",
        "meta": {
            "settings": {
                "number_of_replicas": 0,
                "number_of_shards": 5,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "filter": [
                                "lowercase"
                            ],
                            "type": "custom",
                            "tokenizer": "whitespace"
                        }
                    }
                }
            }
        }
    }
]
