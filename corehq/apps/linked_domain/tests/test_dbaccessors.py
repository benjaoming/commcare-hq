from unittest.mock import patch

from django.test import SimpleTestCase

from corehq.apps.linked_domain.dbaccessors import (
    get_available_domains_to_link,
    get_available_upstream_domains,
)
from corehq.privileges import LITE_RELEASE_MANAGEMENT, RELEASE_MANAGEMENT
from corehq.util.test_utils import flag_enabled


@patch('corehq.apps.users.models.CouchUser')
class TestGetAvailableUpstreamDomains(SimpleTestCase):

    def setUp(self):
        super().setUp()
        self.expected_domains = ['upstream-1', 'upstream-2']

        privilege_patcher = patch('corehq.apps.linked_domain.dbaccessors.domain_has_privilege')
        self.mock_domain_has_privilege = privilege_patcher.start()
        self.addCleanup(privilege_patcher.stop)

        account_patcher = patch(
            'corehq.apps.linked_domain.dbaccessors.get_available_upstream_domains_for_enterprise'
        )
        self.mock_available_account_domains = account_patcher.start()
        self.addCleanup(account_patcher.stop)

        user_patcher = patch('corehq.apps.linked_domain.dbaccessors.get_available_upstream_domains_for_user')
        self.mock_available_user_domains = user_patcher.start()
        self.addCleanup(user_patcher.stop)

        enterprise_patcher = patch('corehq.apps.linked_domain.dbaccessors.domain_is_enterprise')
        self.mock_is_enterprise = enterprise_patcher.start()
        self.mock_is_enterprise.return_value = False
        self.addCleanup(enterprise_patcher.stop)

    def test_returns_empty_if_no_privilege_or_feature_flag(self, mock_user):
        self.mock_domain_has_privilege.return_value = False

        upstream_domains = get_available_upstream_domains('downstream-1', mock_user)

        self.assertFalse(upstream_domains)

    def test_returns_domains_for_account_if_enterprise_and_release_management_privilege(self, mock_user):
        self.mock_is_enterprise.return_value = True
        self.mock_domain_has_privilege.side_effect = lambda domain, privilege: privilege == RELEASE_MANAGEMENT
        self.mock_available_account_domains.return_value = self.expected_domains

        upstream_domains = get_available_upstream_domains('downstream-1', mock_user)

        self.assertEqual(upstream_domains, self.expected_domains)

    def test_returns_domains_for_user_if_not_enterprise_and_release_management_privilege(self, mock_user):
        self.mock_is_enterprise.return_value = False
        self.mock_domain_has_privilege.side_effect = lambda domain, privilege: privilege == RELEASE_MANAGEMENT
        self.mock_available_user_domains.return_value = self.expected_domains

        upstream_domains = get_available_upstream_domains('downstream-1', mock_user)

        self.assertEqual(upstream_domains, self.expected_domains)

    def test_returns_admin_domains_for_user_if_lite_release_management_privilege(self, mock_user):
        self.mock_domain_has_privilege.side_effect = lambda domain, privilege: privilege == LITE_RELEASE_MANAGEMENT
        self.mock_available_user_domains.return_value = self.expected_domains

        upstream_domains = get_available_upstream_domains('downstream-1', mock_user)

        self.mock_available_user_domains.assert_called_with('downstream-1', mock_user, should_enforce_admin=True)
        self.assertEqual(upstream_domains, self.expected_domains)

    @flag_enabled("LINKED_DOMAINS")
    def test_returns_domains_for_user_if_linked_domains_flag(self, mock_user):
        self.mock_domain_has_privilege.return_value = False
        self.mock_available_user_domains.return_value = self.expected_domains

        upstream_domains = get_available_upstream_domains('downstream-1', mock_user)

        self.mock_available_user_domains.assert_called_with('downstream-1', mock_user, should_enforce_admin=False)
        self.assertEqual(upstream_domains, self.expected_domains)


@patch('corehq.apps.users.models.CouchUser')
class TestGetAvailableDomainsToLink(SimpleTestCase):

    def setUp(self):
        super().setUp()
        self.expected_domains = ['downstream-1', 'downstream-2']

        privilege_patcher = patch('corehq.apps.linked_domain.dbaccessors.domain_has_privilege')
        self.mock_domain_has_privilege = privilege_patcher.start()
        self.addCleanup(privilege_patcher.stop)

        account_patcher = patch(
            'corehq.apps.linked_domain.dbaccessors.get_available_domains_to_link_for_enterprise'
        )
        self.mock_available_account_domains = account_patcher.start()
        self.addCleanup(account_patcher.stop)

        user_patcher = patch('corehq.apps.linked_domain.dbaccessors.get_available_domains_to_link_for_user')
        self.mock_available_user_domains = user_patcher.start()
        self.addCleanup(user_patcher.stop)

        enterprise_patcher = patch('corehq.apps.linked_domain.dbaccessors.domain_is_enterprise')
        self.mock_is_enterprise = enterprise_patcher.start()
        self.mock_is_enterprise.return_value = False
        self.addCleanup(enterprise_patcher.stop)

    def test_returns_empty_if_no_privilege_or_feature_flag(self, mock_user):
        self.mock_domain_has_privilege.return_value = False

        domains = get_available_domains_to_link('upstream', mock_user)

        self.assertFalse(domains)

    def test_returns_domains_for_account_if_enterprise_and_release_management_privilege(self, mock_user):
        self.mock_is_enterprise.return_value = True
        self.mock_domain_has_privilege.return_value = True
        self.mock_available_account_domains.return_value = self.expected_domains
        self.mock_available_user_domains.return_value = ['wrong']

        domains = get_available_domains_to_link('upstream', mock_user)

        self.assertEqual(domains, self.expected_domains)

    def test_returns_domains_for_user_if_not_enterprise_and_release_management_privilege(self, mock_user):
        self.mock_is_enterprise.return_value = False
        self.mock_domain_has_privilege.return_value = True
        self.mock_available_user_domains.return_value = self.expected_domains
        self.mock_available_account_domains.return_value = ['wrong']

        domains = get_available_domains_to_link('upstream', mock_user)

        self.assertEqual(domains, self.expected_domains)

    def test_returns_admin_domains_for_users_if_lite_release_management_privilege(self, mock_user):
        self.mock_domain_has_privilege.side_effect = lambda domain, privilege: privilege == LITE_RELEASE_MANAGEMENT
        self.mock_available_user_domains.return_value = self.expected_domains
        self.mock_available_account_domains.return_value = ['wrong']

        domains = get_available_domains_to_link('upstream', mock_user)

        self.mock_available_user_domains.assert_called_with('upstream', mock_user, should_enforce_admin=True)
        self.assertEqual(domains, self.expected_domains)

    @flag_enabled("LINKED_DOMAINS")
    def test_returns_domains_for_user_for_linked_domains_flag(self, mock_user):
        self.mock_domain_has_privilege.return_value = False
        self.mock_available_user_domains.return_value = self.expected_domains
        self.mock_available_account_domains.return_value = ['wrong']

        domains = get_available_domains_to_link('upstream', mock_user)

        self.mock_available_user_domains.assert_called_with('upstream', mock_user, should_enforce_admin=False)
        self.assertEqual(domains, self.expected_domains)
