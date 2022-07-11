from django import forms
from django.test import SimpleTestCase, override_settings

from corehq.apps.domain.forms import clean_password


@override_settings(MINIMUM_PASSWORD_LENGTH=0, MINIMUM_ZXCVBN_SCORE=2)
class PasswordStrengthTest(SimpleTestCase):

    # Test zxcvbn library strength
    def test_score_0_password(self):
        self.assert_bad_password(PASSWORDS_BY_STRENGTH[0])

    def test_score_1_password(self):
        self.assert_bad_password(PASSWORDS_BY_STRENGTH[1])

    def test_score_2_password(self):
        self.assert_good_password(PASSWORDS_BY_STRENGTH[2])

    def test_score_3_password(self):
        self.assert_good_password(PASSWORDS_BY_STRENGTH[3])

    def test_score_4_password(self):
        self.assert_good_password(PASSWORDS_BY_STRENGTH[4])

    @override_settings(MINIMUM_ZXCVBN_SCORE=3)
    def test_sensitivity_to_minimum_zxcvbn_score_setting_bad(self):
        self.assert_bad_password(PASSWORDS_BY_STRENGTH[2])

    @override_settings(MINIMUM_ZXCVBN_SCORE=3)
    def test_sensitivity_to_minimum_zxcvbn_score_setting_good(self):
        self.assert_good_password(PASSWORDS_BY_STRENGTH[3])

    # Test minimum password length
    @override_settings(MINIMUM_PASSWORD_LENGTH=8, MINIMUM_ZXCVBN_SCORE=0)
    def test_length_5_password(self):
        self.assert_bad_password("e3r4f")

    # Password has less than the minimum requirement
    @override_settings(MINIMUM_PASSWORD_LENGTH=7)
    def test_score_1_length_9_password(self):
        self.assert_bad_password(PASSWORDS_BY_STRENGTH[1])

    # Password has exactly the minimum requirement
    @override_settings(MINIMUM_PASSWORD_LENGTH=7)
    def test_score_2_length_7_password(self):
        self.assert_good_password(PASSWORDS_BY_STRENGTH[2])

    # Password has more than the minimum requirement
    @override_settings(MINIMUM_SUBSCRIPTION_LENGTH=8)
    def test_score_3_length_10_password(self):
        self.assert_good_password(PASSWORDS_BY_STRENGTH[3])

    def assert_good_password(self, password):
        self.assertEqual(clean_password(password), password)

    def assert_bad_password(self, password):
        with self.assertRaises(forms.ValidationError):
            clean_password(password)


PASSWORDS_BY_STRENGTH = {
    0: 's3cr3t',
    1: 'password7',
    2: 'aljfzpo',
    3: '1234mna823',
    4: ')(^#:LKNVA^',
}
