import re
from collections import defaultdict

from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from dimagi.utils.logging import notify_exception

from corehq.apps.app_manager.dbaccessors import get_app_cached
from corehq.apps.app_manager.util import module_offers_search
from corehq.apps.case_search.const import (
    CASE_SEARCH_MAX_RESULTS,
    COMMCARE_PROJECT,
)
from corehq.apps.case_search.exceptions import CaseSearchUserError, CaseFilterError, TooManyRelatedCasesError
from corehq.apps.case_search.filter_dsl import (
    build_filter_from_xpath,
)
from corehq.apps.case_search.models import (
    CASE_SEARCH_BLACKLISTED_OWNER_ID_KEY,
    CASE_SEARCH_XPATH_QUERY_KEY,
    UNSEARCHABLE_KEYS,
    CaseSearchConfig,
    extract_search_request_config,
)
from corehq.apps.es import case_search, filters, queries
from corehq.apps.es.case_search import (
    CaseSearchES,
    case_property_missing,
    case_property_query,
    case_property_range_query,
    wrap_case_search_hit,
    reverse_index_case_query,
)
from corehq.apps.registry.exceptions import (
    RegistryAccessException,
    RegistryNotFound,
)
from corehq.apps.registry.helper import DataRegistryHelper


def get_case_search_results_from_request(domain, app_id, couch_user, request_dict):
    config = extract_search_request_config(request_dict)
    return get_case_search_results(
        domain,
        config.case_types,
        config.criteria,
        app_id=app_id,
        couch_user=couch_user,
        registry_slug=config.data_registry,
        custom_related_case_property=config.custom_related_case_property,
    )


def get_case_search_results(domain, case_types, criteria,
                            app_id=None, couch_user=None, registry_slug=None, custom_related_case_property=None):
    if registry_slug:
        query_domains = _get_registry_visible_domains(couch_user, domain, case_types, registry_slug)
        helper = _RegistryQueryHelper(domain, query_domains)
    else:
        query_domains = [domain]
        helper = _QueryHelper(domain)

    builder = CaseSearchQueryBuilder(domain, case_types, query_domains)
    try:
        search_es = builder.build_query(criteria)
    except TooManyRelatedCasesError:
        raise CaseSearchUserError(_('Search has too many results. Please try a more specific search.'))
    except CaseFilterError as e:
        # This is an app building error, notify so we can track
        notify_exception(None, str(e), details=dict(
            exception_type=type(e),
        ))
        raise CaseSearchUserError(str(e))

    try:
        hits = search_es.run().raw_hits
    except Exception as e:
        notify_exception(None, str(e), details=dict(
            exception_type=type(e),
        ))
        raise

    cases = [helper.wrap_case(hit, include_score=True) for hit in hits]
    if app_id:
        cases.extend(get_related_cases(helper, app_id, case_types, cases, custom_related_case_property))
    return cases


def _get_registry_visible_domains(couch_user, domain, case_types, registry_slug):
    try:
        helper = DataRegistryHelper(domain, registry_slug=registry_slug)
        helper.check_data_access(couch_user, case_types)
    except (RegistryNotFound, RegistryAccessException):
        return [domain]
    else:
        return helper.visible_domains


class _QueryHelper:
    def __init__(self, domain):
        self.domain = domain

    def get_base_queryset(self):
        return CaseSearchES().domain(self.domain)

    def wrap_case(self, es_hit, include_score=False, is_related_case=False):
        return wrap_case_search_hit(es_hit, include_score=include_score, is_related_case=is_related_case)


class _RegistryQueryHelper:
    def __init__(self, domain, query_domains):
        self.domain = domain
        self.query_domains = query_domains

    def get_base_queryset(self):
        return CaseSearchES().domain(self.query_domains)

    def wrap_case(self, es_hit, include_score=False, is_related_case=False):
        case = wrap_case_search_hit(es_hit, include_score=include_score, is_related_case=is_related_case)
        case.case_json[COMMCARE_PROJECT] = case.domain
        return case


class CaseSearchQueryBuilder:
    """Compiles the case search object for the view"""

    def __init__(self, domain, case_types, query_domains=None):
        self.request_domain = domain
        self.case_types = case_types
        self.query_domains = [domain] if query_domains is None else query_domains

    @cached_property
    def config(self):
        try:
            config = (CaseSearchConfig.objects
                      .prefetch_related('fuzzy_properties')
                      .prefetch_related('ignore_patterns')
                      .get(domain=self.request_domain))
        except CaseSearchConfig.DoesNotExist as e:
            from corehq.util.soft_assert import soft_assert
            _soft_assert = soft_assert(
                to="{}@{}.com".format('frener', 'dimagi'),
                notify_admins=False, send_to_ops=False
            )
            _soft_assert(
                False,
                "Someone in domain: {} tried accessing case search without a config".format(self.request_domain),
                e
            )
            config = CaseSearchConfig(domain=self.request_domain)
        return config

    def build_query(self, search_criteria):
        search_es = self._get_initial_search_es()
        for criteria in search_criteria:
            search_es = self._apply_filter(search_es, criteria)
        return search_es

    def _get_initial_search_es(self):
        return (CaseSearchES()
                .domain(self.query_domains)
                .case_type(self.case_types)
                .is_closed(False)
                .size(CASE_SEARCH_MAX_RESULTS)
                .set_sorting_block(['_score', '_doc']))

    def _apply_filter(self, search_es, criteria):
        if criteria.key == CASE_SEARCH_XPATH_QUERY_KEY:
            if not criteria.is_empty:
                if criteria.has_multiple_terms:
                    for value in criteria.value:
                        search_es = search_es.filter(build_filter_from_xpath(self.query_domains, value))
                    return search_es
                else:
                    return search_es.filter(build_filter_from_xpath(self.query_domains, criteria.value))
        elif criteria.key == 'owner_id':
            if not criteria.is_empty:
                return search_es.filter(case_search.owner(criteria.value))
        elif criteria.key == CASE_SEARCH_BLACKLISTED_OWNER_ID_KEY:
            if not criteria.is_empty:
                return search_es.filter(case_search.blacklist_owner_id(criteria.value_as_list))
        elif criteria.key == COMMCARE_PROJECT:
            if not criteria.is_empty:
                return search_es.filter(filters.domain(criteria.value))
        elif criteria.key not in UNSEARCHABLE_KEYS:
            return search_es.add_query(self._get_case_property_query(criteria), queries.MUST)
        return search_es

    def _get_daterange_query(self, criteria):
        startdate, enddate = criteria.get_date_range()
        return case_property_range_query(criteria.key, gte=startdate, lte=enddate)

    def _get_case_property_query(self, criteria):
        if criteria.has_multiple_terms and criteria.has_missing_filter:
            non_blank_criteria = criteria.clone_without_blanks()
            return self._get_case_property_or_missing_query(non_blank_criteria)
        else:
            return self._get_query(criteria)

    def _get_case_property_or_missing_query(self, criteria):
        if criteria.is_empty:
            return case_property_missing(criteria.key)

        if criteria.is_ancestor_query:
            missing_filter = build_filter_from_xpath(self.query_domains, f'{criteria.key} = ""')
        else:
            missing_filter = case_property_missing(criteria.key)
        return filters.OR(self._get_query(criteria), missing_filter)

    def _get_query(self, criteria):
        if criteria.is_daterange:
            return self._get_daterange_query(criteria)

        value = self._remove_ignored_patterns(criteria.key, criteria.value)
        fuzzy = criteria.key in self._fuzzy_properties
        if criteria.is_ancestor_query:
            query = f'{criteria.key} = "{value}"'
            return build_filter_from_xpath(self.query_domains, query, fuzzy=fuzzy)
        elif criteria.is_index_query:
            return reverse_index_case_query(value, criteria.index_query_identifier)
        else:
            return case_property_query(criteria.key, value, fuzzy=fuzzy)

    def _remove_ignored_patterns(self, case_property, value):
        for to_remove in self._patterns_to_remove[case_property]:
            if isinstance(value, list):
                value = [re.sub(to_remove, '', val) for val in value]
            else:
                value = re.sub(to_remove, '', value)
        return value

    @cached_property
    def _patterns_to_remove(self):
        patterns_by_property = defaultdict(list)
        for pattern in self.config.ignore_patterns.filter(
                domain=self.request_domain,
                case_type__in=self.case_types,
        ):
            patterns_by_property[pattern.case_property].append(re.escape(pattern.regex))
        return patterns_by_property

    @cached_property
    def _fuzzy_properties(self):
        return [
            prop for properties_config in
            self.config.fuzzy_properties.filter(domain=self.request_domain,
                                                case_type__in=self.case_types)
            for prop in properties_config.properties
        ]


def get_related_cases(helper, app_id, case_types, cases, custom_related_case_property):
    """
    Fetch related cases that are necessary to display any related-case
    properties in the app requesting this case search.

    Returns list of CommCareCase objects for adding to CaseDBFixture.
    """
    if not cases:
        return []

    app = get_app_cached(helper.domain, app_id)
    paths = [
        rel for rels in [get_related_case_relationships(app, case_type) for case_type in case_types]
        for rel in rels
    ]
    child_case_types = [
        _type for types in [get_child_case_types(app, case_type) for case_type in case_types]
        for _type in types
    ]

    expanded_case_results = []
    if custom_related_case_property:
        expanded_case_results.extend(get_expanded_case_results(helper, custom_related_case_property, cases))

    results = expanded_case_results
    top_level_cases = cases + expanded_case_results
    if paths:
        results.extend(get_related_case_results(helper, top_level_cases, paths))

    if child_case_types:
        results.extend(get_child_case_results(helper, top_level_cases, child_case_types))

    initial_case_ids = {case.case_id for case in cases}
    return list({
        case.case_id: case for case in results if case.case_id not in initial_case_ids
    }.values())


def get_related_case_relationships(app, case_type):
    """
    Get unique case relationships used by search details in any modules that
    match the given case type and are configured for case search.

    Returns a set of relationships, e.g. {"parent", "host", "parent/parent"}
    """
    paths = set()
    for module in app.get_modules():
        if module.case_type == case_type and module_offers_search(module):
            for column in module.search_detail("short").columns + module.search_detail("long").columns:
                if not column.useXpathExpression:
                    parts = column.field.split("/")
                    if len(parts) > 1:
                        parts.pop()     # keep only the relationship: "parent", "parent/parent", etc.
                        paths.add("/".join(parts))
    return paths


def get_related_case_results(helper, cases, paths):
    """
    Given a set of cases and a set of case property paths,
    fetches ES documents for all cases referenced by those paths.
    """
    if not cases:
        return []

    results_cache = {}
    for path in paths:
        current_cases = cases
        parts = path.split("/")
        for index, identifier in enumerate(parts):
            fragment = "/".join(parts[:index + 1])
            if fragment in results_cache:
                current_cases = results_cache[fragment]
            else:
                indices = [case.get_index(identifier) for case in current_cases]
                related_case_ids = {i.referenced_id for i in indices if i}
                current_cases = _get_case_search_cases(helper, related_case_ids)
                results_cache[fragment] = current_cases

    results = []
    for path in paths:
        results.extend(results_cache[path])

    return results


def get_child_case_types(app, case_type):
    """
    Get child case types used by search detail tab nodesets in any modules
    that match the given case type and are configured for case search.

    Returns a set of case types
    """
    case_types = set()
    for module in app.get_modules():
        if module.case_type == case_type and module_offers_search(module):
            for tab in module.search_detail("long").tabs:
                if tab.has_nodeset and tab.nodeset_case_type:
                    case_types.add(tab.nodeset_case_type)

    return case_types


def get_child_case_results(helper, parent_cases, case_types):
    parent_case_ids = {c.case_id for c in parent_cases}
    results = (helper.get_base_queryset()
               .case_type(case_types)
               .get_child_cases(parent_case_ids, "parent")
               .run().hits)
    return [helper.wrap_case(result, is_related_case=True) for result in results]


def get_expanded_case_results(helper, custom_related_case_property, cases):
    expanded_case_ids = {
        case.get_case_property(custom_related_case_property, dynamic_only=True) for case in cases
    }
    expanded_case_ids -= {None, ""}
    return _get_case_search_cases(helper, expanded_case_ids)


def _get_case_search_cases(helper, case_ids):
    results = helper.get_base_queryset().case_ids(case_ids).run().hits
    return [helper.wrap_case(result, is_related_case=True) for result in results]
