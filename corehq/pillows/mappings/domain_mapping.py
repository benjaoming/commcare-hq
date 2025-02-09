from pillowtop.es_utils import DOMAIN_HQ_INDEX_NAME, ElasticsearchIndexInfo

from corehq.apps.es.client import Tombstone
from corehq.apps.es.domains import domain_adapter
from corehq.pillows.core import DATE_FORMATS_ARR, DATE_FORMATS_STRING
from corehq.util.elastic import prefix_for_tests

DOMAIN_INDEX = domain_adapter.index_name
DOMAIN_ES_ALIAS = prefix_for_tests('hqdomains')

DOMAIN_MAPPING = {
    "_all": {
        "enabled": False
    },
    "_meta": {
        "comment": "",
        "created": None
    },
    "date_detection": False,
    "date_formats": DATE_FORMATS_ARR,
    "dynamic": False,
    "properties": {
        "allow_domain_requests": {
            "type": "boolean"
        },
        "area": {
            "type": "string"
        },
        "attribution_notes": {
            "type": "string"
        },
        "author": {
            "fields": {
                "author": {
                    "index": "analyzed",
                    "type": "string"
                },
                "exact": {
                    "index": "not_analyzed",
                    "type": "string"
                }
            },
            "type": "multi_field"
        },
        "cached_properties": {
            "dynamic": False,
            "type": "object"
        },
        "call_center_config": {
            "dynamic": False,
            "type": "object",
            "properties": {
                "case_owner_id": {
                    "type": "string"
                },
                "case_type": {
                    "type": "string"
                },
                "doc_type": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "enabled": {
                    "type": "boolean"
                },
                "use_fixtures": {
                    "type": "boolean"
                }
            }
        },
        "case_display": {
            "dynamic": False,
            "type": "object",
            "properties": {
                "case_details": {
                    "dynamic": False,
                    "type": "object"
                },
                "doc_type": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "form_details": {
                    "dynamic": False,
                    "type": "object"
                }
            }
        },
        "case_sharing": {
            "type": "boolean"
        },
        "cda": {
            "dynamic": False,
            "type": "object",
            "properties": {
                "date": {
                    "format": DATE_FORMATS_STRING,
                    "type": "date"
                },
                "doc_type": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "signed": {
                    "type": "boolean"
                },
                "type": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "user_id": {
                    "type": "string"
                },
                "user_ip": {
                    "type": "string"
                },
                "version": {
                    "type": "string"
                }
            }
        },
        "commtrack_enabled": {
            "type": "boolean"
        },
        "copy_history": {
            "type": "string"
        },
        "cp_300th_form_submission": {
            "format": DATE_FORMATS_STRING,
            "type": "date"
        },
        "cp_first_domain_for_user": {
            "type": "boolean"
        },
        "cp_first_form": {
            "format": DATE_FORMATS_STRING,
            "type": "date"
        },
        "cp_has_app": {
            "type": "boolean"
        },
        "cp_is_active": {
            "type": "boolean"
        },
        "cp_j2me_90_d_bool": {
            "type": "boolean"
        },
        "cp_last_form": {
            "format": DATE_FORMATS_STRING,
            "type": "date"
        },
        "cp_last_updated": {
            "format": DATE_FORMATS_STRING,
            "type": "date"
        },
        "cp_n_30_day_cases": {
            "type": "long"
        },
        "cp_n_60_day_cases": {
            "type": "long"
        },
        "cp_n_90_day_cases": {
            "type": "long"
        },
        "cp_n_active_cases": {
            "type": "long"
        },
        "cp_n_active_cc_users": {
            "type": "long"
        },
        "cp_n_cases": {
            "type": "long"
        },
        "cp_n_cc_users": {
            "type": "long"
        },
        "cp_n_forms": {
            "type": "long"
        },
        "cp_n_forms_30_d": {
            "type": "long"
        },
        "cp_n_forms_60_d": {
            "type": "long"
        },
        "cp_n_forms_90_d": {
            "type": "long"
        },
        "cp_n_in_sms": {
            "type": "long"
        },
        "cp_n_inactive_cases": {
            "type": "long"
        },
        "cp_n_j2me_30_d": {
            "type": "long"
        },
        "cp_n_j2me_60_d": {
            "type": "long"
        },
        "cp_n_j2me_90_d": {
            "type": "long"
        },
        "cp_n_out_sms": {
            "type": "long"
        },
        "cp_n_sms_30_d": {
            "type": "long"
        },
        "cp_n_sms_60_d": {
            "type": "long"
        },
        "cp_n_sms_90_d": {
            "type": "long"
        },
        "cp_n_sms_ever": {
            "type": "long"
        },
        "cp_n_sms_in_30_d": {
            "type": "long"
        },
        "cp_n_sms_in_60_d": {
            "type": "long"
        },
        "cp_n_sms_in_90_d": {
            "type": "long"
        },
        "cp_n_sms_out_30_d": {
            "type": "long"
        },
        "cp_n_sms_out_60_d": {
            "type": "long"
        },
        "cp_n_sms_out_90_d": {
            "type": "long"
        },
        "cp_n_users_submitted_form": {
            "type": "long"
        },
        "cp_n_web_users": {
            "type": "long"
        },
        "cp_sms_30_d": {
            "type": "boolean"
        },
        "cp_sms_ever": {
            "type": "boolean"
        },
        "creating_user": {
            "type": "string"
        },
        "date_created": {
            "format": DATE_FORMATS_STRING,
            "type": "date"
        },
        "default_timezone": {
            "type": "string"
        },
        "deployment": {
            "dynamic": False,
            "type": "object",
            "properties": {
                "city": {
                    "fields": {
                        "city": {
                            "index": "analyzed",
                            "type": "string"
                        },
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "countries": {
                    "fields": {
                        "countries": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "description": {
                    "fields": {
                        "description": {
                            "index": "analyzed",
                            "type": "string"
                        },
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "doc_type": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "public": {
                    "type": "boolean"
                },
                "region": {
                    "fields": {
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "region": {
                            "index": "analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                }
            }
        },
        "description": {
            "type": "string"
        },
        "doc_type": {
            "index": "not_analyzed",
            "type": "string"
        },
        "downloads": {
            "type": "long"
        },
        "full_downloads": {
            "type": "long"
        },
        "hipaa_compliant": {
            "type": "boolean"
        },
        "hr_name": {
            "type": "string"
        },
        "internal": {
            "dynamic": False,
            "type": "object",
            "properties": {
                "area": {
                    "fields": {
                        "area": {
                            "index": "analyzed",
                            "type": "string"
                        },
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "can_use_data": {
                    "type": "boolean"
                },
                "commcare_edition": {
                    "type": "string"
                },
                "commconnect_domain": {
                    "type": "boolean"
                },
                "commtrack_domain": {
                    "type": "boolean"
                },
                "custom_eula": {
                    "type": "boolean"
                },
                "doc_type": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "goal_followup_rate": {
                    "type": "double"
                },
                "goal_time_period": {
                    "type": "long"
                },
                "initiative": {
                    "fields": {
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "initiative": {
                            "index": "analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "notes": {
                    "type": "string"
                },
                "organization_name": {
                    "fields": {
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "organization_name": {
                            "index": "analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "phone_model": {
                    "fields": {
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "phone_model": {
                            "index": "analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "platform": {
                    "type": "string"
                },
                "project_manager": {
                    "type": "string"
                },
                "project_state": {
                    "type": "string"
                },
                "self_started": {
                    "type": "boolean"
                },
                "sf_account_id": {
                    "type": "string"
                },
                "sf_contract_id": {
                    "type": "string"
                },
                "sub_area": {
                    "fields": {
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "sub_area": {
                            "index": "analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                },
                "using_adm": {
                    "type": "boolean"
                },
                "using_call_center": {
                    "type": "boolean"
                },
                "workshop_region": {
                    "fields": {
                        "exact": {
                            "index": "not_analyzed",
                            "type": "string"
                        },
                        "workshop_region": {
                            "index": "analyzed",
                            "type": "string"
                        }
                    },
                    "type": "multi_field"
                }
            }
        },
        "is_active": {
            "type": "boolean"
        },
        "is_approved": {
            "type": "boolean"
        },
        "is_shared": {
            "type": "boolean"
        },
        "is_sms_billable": {
            "type": "boolean"
        },
        "is_snapshot": {
            "type": "boolean"
        },
        "is_starter_app": {
            "type": "boolean"
        },
        "is_test": {
            "type": "string"
        },
        "last_modified": {
            "format": DATE_FORMATS_STRING,
            "type": "date"
        },
        "license": {
            "type": "string"
        },
        "migrations": {
            "dynamic": False,
            "type": "object",
            "properties": {
                "doc_type": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "has_migrated_permissions": {
                    "type": "boolean"
                }
            }
        },
        "multimedia_included": {
            "type": "boolean"
        },
        "name": {
            "fields": {
                "exact": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "name": {
                    "index": "analyzed",
                    "type": "string"
                }
            },
            "type": "multi_field"
        },
        "organization": {
            "type": "string"
        },
        "phone_model": {
            "type": "string"
        },
        "project_type": {
            "analyzer": "comma",
            "type": "string"
        },
        "published": {
            "type": "boolean"
        },
        "publisher": {
            "type": "string"
        },
        "restrict_superusers": {
            "type": "boolean"
        },
        "secure_submissions": {
            "type": "boolean"
        },
        "short_description": {
            "fields": {
                "exact": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "short_description": {
                    "index": "analyzed",
                    "type": "string"
                }
            },
            "type": "multi_field"
        },
        "sms_case_registration_enabled": {
            "type": "boolean"
        },
        "sms_case_registration_owner_id": {
            "type": "string"
        },
        "sms_case_registration_type": {
            "type": "string"
        },
        "sms_case_registration_user_id": {
            "type": "string"
        },
        "sms_mobile_worker_registration_enabled": {
            "type": "boolean"
        },
        "snapshot_head": {
            "type": "boolean"
        },
        "snapshot_time": {
            "format": DATE_FORMATS_STRING,
            "type": "date"
        },
        "sub_area": {
            "type": "string"
        },
        "subscription": {
            "type": "string"
        },
        "survey_management_enabled": {
            "type": "boolean"
        },
        "tags": {
            "type": "string"
        },
        "title": {
            "fields": {
                "exact": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "title": {
                    "index": "analyzed",
                    "type": "string"
                }
            },
            "type": "multi_field"
        },
        "use_sql_backend": {
            "type": "boolean"
        },
        "yt_id": {
            "type": "string"
        },
        Tombstone.PROPERTY_NAME: {
            "type": "boolean"
        }
    }
}


DOMAIN_INDEX_INFO = ElasticsearchIndexInfo(
    index=DOMAIN_INDEX,
    alias=DOMAIN_ES_ALIAS,
    type=domain_adapter.type,
    mapping=DOMAIN_MAPPING,
    hq_index_name=DOMAIN_HQ_INDEX_NAME
)
