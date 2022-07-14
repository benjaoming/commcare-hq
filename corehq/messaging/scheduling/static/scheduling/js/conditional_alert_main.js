hqDefine("scheduling/js/conditional_alert_main", [
    'jquery',
    'underscore',
    'knockout',
    'hqwebapp/js/initial_page_data',
    'data_interfaces/js/case_rule_criteria',
    'hqwebapp/js/widgets',
    'scheduling/js/create_schedule.ko',
    'data_interfaces/js/make_read_only',
], function (
    $,
    _,
    ko,
    initialPageData,
    CaseRuleCriteria
) {
    function BasicInformationTab(name) {
        var self = {};
        self.name = ko.observable(name);
        self.basicTabValid = ko.computed(function () {
            return !_.isEmpty(self.name().trim());
        });
        self.setRuleTabVisibility = function () {
            if (self.basicTabValid()) {
                $("#rule-nav").removeClass("hidden");
            }
        };
        self.navigateToNav = function (navId) {
            $(navId).find('a').trigger('click');
        };
        self.handleBasicNavContinue = function () {
            $("#rule-nav").removeClass("hidden");
            $('#rule-nav').find('a').trigger('click');
        };
        self.setRuleTabVisibility();
        return self;
    }

    $(function () {
        $("#conditional-alert-basic-info-panel").koApplyBindings(BasicInformationTab(
            initialPageData.get('rule_name')
        ));

        $('#rule-criteria-panel').koApplyBindings(CaseRuleCriteria(
            initialPageData.get('criteria_initial'),
            initialPageData.get('criteria_constants'),
            initialPageData.get('all_case_properties')
        ));
    });
});
