"""
UserES
------

Here's an example adapted from the case list report - it gets a list of the ids
of all unknown users, web users, and demo users on a domain.

.. code-block:: python

    from corehq.apps.es import users as user_es

    user_filters = [
        user_es.unknown_users(),
        user_es.web_users(),
        user_es.demo_users(),
    ]

    query = (user_es.UserES()
             .domain(self.domain)
             .OR(*user_filters)
             .show_inactive())

    owner_ids = query.get_ids()
"""
from . import filters, queries
from .client import ElasticDocumentAdapter, create_document_adapter
from .es_query import HQESQuery
from .index.settings import IndexSettingsKey
from .transient_util import get_adapter_mapping, from_dict_with_possible_id


class UserES(HQESQuery):
    index = 'users'
    default_filters = {
        'not_deleted': filters.term("base_doc", "couchuser"),
        'active': filters.term("is_active", True),
    }

    @property
    def builtin_filters(self):
        return [
            domain,
            domains,
            created,
            mobile_users,
            web_users,
            user_ids,
            primary_location,
            location,
            last_logged_in,
            analytics_enabled,
            is_practice_user,
            role_id,
            is_active,
            username,
            metadata,
        ] + super(UserES, self).builtin_filters

    def show_inactive(self):
        """Include inactive users, which would normally be filtered out."""
        return self.remove_default_filter('active')

    def show_only_inactive(self):
        query = self.remove_default_filter('active')
        return query.is_active(False)


class ElasticUser(ElasticDocumentAdapter):

    settings_key = IndexSettingsKey.USERS

    @property
    def mapping(self):
        return get_adapter_mapping(self)

    @classmethod
    def from_python(cls, doc):
        return from_dict_with_possible_id(doc)


user_adapter = create_document_adapter(
    ElasticUser,
    "hqusers_2017-09-07",
    "user",
)


def domain(domain, allow_enterprise=False):
    domain_list = [domain]
    if allow_enterprise:
        from corehq.apps.enterprise.models import EnterprisePermissions
        config = EnterprisePermissions.get_by_domain(domain)
        if config.is_enabled and domain in config.domains:
            domain_list.append(config.source_domain)
    return domains(domain_list)


def domains(domains):
    return filters.OR(
        filters.term("domain.exact", domains),
        filters.term("domain_memberships.domain.exact", domains)
    )


def analytics_enabled(enabled=True):
    if enabled:
        return filters.OR(
            filters.term("analytics_enabled", True),
            filters.missing("analytics_enabled")
        )
    else:
        return filters.term("analytics_enabled", False)


def username(username):
    return filters.term("username.exact", username)


def web_users():
    return filters.doc_type("WebUser")


def mobile_users():
    return filters.doc_type("CommCareUser")


def unknown_users():
    """
    Return only UnknownUsers.  Unknown users are mock users created from xform
    submissions with unknown user ids.
    """
    return filters.doc_type("UnknownUser")


def admin_users():
    """
    Return only AdminUsers.  Admin users are mock users created from xform
    submissions with unknown user ids whose username is "admin".
    """
    return filters.doc_type("AdminUser")


def demo_users():
    """Matches users whose username is demo_user"""
    return username("demo_user")


def created(gt=None, gte=None, lt=None, lte=None):
    return filters.date_range('created_on', gt, gte, lt, lte)


def last_logged_in(gt=None, gte=None, lt=None, lte=None):
    return filters.date_range('last_login', gt, gte, lt, lte)


def user_ids(user_ids):
    return filters.term("_id", list(user_ids))


def primary_location(location_id):
    # by primary location
    return filters.OR(
        filters.AND(mobile_users(), filters.term('location_id', location_id)),
        filters.AND(
            web_users(),
            filters.term('domain_memberships.location_id', location_id)
        ),
    )


def location(location_id):
    # by any assigned-location primary or not
    return filters.OR(
        filters.AND(mobile_users(), filters.term('assigned_location_ids', location_id)),
        # todo; this actually doesn't get applied since the below field is not indexed
        filters.AND(
            web_users(),
            filters.term('domain_memberships.assigned_location_ids', location_id)
        ),
    )


def is_practice_user(practice_mode=True):
    return filters.term('is_demo_user', practice_mode)


def role_id(role_id):
    return filters.OR(
        filters.term("domain_membership.role_id", role_id),     # mobile users
        filters.term("domain_memberships.role_id", role_id)     # web users
    )


def is_active(active=True):
    return filters.term("is_active", active)


def metadata(key, value):
    # Note that this dict is stored in ES under the `user_data` field, and
    # transformed into a queryable format (in ES) as `user_data_es`, but it's
    # referenced in python as `metadata`
    return queries.nested(
        'user_data_es',
        filters.AND(
            filters.term(field='user_data_es.key', value=key),
            queries.match(field='user_data_es.value', search_string=value),
        )
    )
