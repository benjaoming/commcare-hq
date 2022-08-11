/* global Uint8Array */
hqDefine("app_manager/js/details/case_claim", function () {
    var get = hqImport('hqwebapp/js/initial_page_data').get,
        generateSemiRandomId = function () {
        // https://stackoverflow.com/a/2117523
            return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, function (c) {
                return (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16);
            });
        },
        subscribeToSave = function (model, observableNames, saveButton) {
            _.each(observableNames, function (name) {
                model[name].subscribe(function () {
                    saveButton.fire('change');
                });
            });
            $(".hq-help").hqHelp();
        },
        itemsetValue = function (item) {
            return "instance('" + item.id + "')" + item.path;
        };

    var itemsetModel = function (options, saveButton) {
        options = _.defaults(options, {
            'instance_id': '',
            'instance_uri': '',
            'nodeset': null,
            'label': '',
            'value': '',
            'sort': '',
        });
        var self = ko.mapping.fromJS(options);

        self.lookupTableNodeset = ko.pureComputed({
            write: function (value) {
                if (value === undefined) {
                    self.nodeset(null);
                }
                else {
                    self.instance_id(value);
                    var itemList = _.filter(get('js_options').item_lists, function (item) {
                        return item.id === value;
                    });
                    if (itemList && itemList.length === 1) {
                        self.instance_uri(itemList[0]['uri']);
                        self.nodeset(itemsetValue(itemList[0]));
                    }
                    else {
                        self.nodeset(null);
                    }
                }
            },
            read: function () {
                return self.instance_id();
            },
        });
        self.nodesetValid = ko.computed(function () {
            if (self.nodeset() === null) {
                return true;
            }
            var itemLists = _.map(get('js_options').item_lists, function (item) {
                    return itemsetValue(item);
                });
            if (self.nodeset().split("/").length === 0) {
                return false;
            }
            var instancePart = self.nodeset().split("/")[0];
            for (var i = itemLists.length - 1; i >= 0; i--) {
                var groups = itemLists[i].split("/");
                if (groups.length > 0 && groups[0] === instancePart) {
                    return true;
                }
            }
            return false;
        });
        subscribeToSave(self,
            ['nodeset', 'label', 'value', 'sort', 'instance_uri'], saveButton);

        return self;
    };

    var searchPropertyModel = function (options, saveButton) {
        options = _.defaults(options, {
            name: '',
            label: '',
            hint: '',
            appearance: '',
            isMultiselect: false,
            allowBlankValue: false,
            defaultValue: '',
            hidden: false,
            receiverExpression: '',
            itemsetOptions: {},
            exclude: false,
            requiredTest: '',
            requiredText: '',
            validationTest: '',
            validationText: '',
        });
        var self = {};
        self.uniqueId = generateSemiRandomId();
        self.name = ko.observable(options.name);
        self.label = ko.observable(options.label);
        self.hint = ko.observable(options.hint);
        self.appearance = ko.observable(options.appearance);
        self.isMultiselect = ko.observable(options.isMultiselect);
        self.allowBlankValue = ko.observable(options.allowBlankValue);
        self.defaultValue = ko.observable(options.defaultValue);
        self.hidden = ko.observable(options.hidden);
        self.exclude = ko.observable(options.exclude);
        self.requiredTest = ko.observable(options.requiredTest);
        self.requiredText = ko.observable(options.requiredText);
        self.validationTest = ko.observable(options.validationTest);
        self.validationText = ko.observable(options.validationText);
        self.appearanceFinal = ko.computed(function () {
            var appearance = self.appearance();
            if (appearance === 'report_fixture' || appearance === 'lookup_table_fixture') {
                return 'fixture';
            }
            else {
                return appearance;
            }
        });
        self.dropdownLabels = ko.computed(function () {
            if (self.appearance() === 'report_fixture') {
                return {
                    'labelPlaceholder': 'column_0',
                    'valuePlaceholder': 'column_0',
                    'optionsLabel': gettext("Mobile UCR Options"),
                    'tableLabel': gettext("Mobile UCR Report"),
                    'selectLabel': gettext("Select a Report..."),
                    'advancedLabel': gettext("Advanced Mobile UCR Options"),
                };
            }
            else {
                return {
                    'labelPlaceholder': 'name',
                    'valuePlaceholder': 'id',
                    'optionsLabel': gettext("Lookup Table Options"),
                    'tableLabel': gettext("Lookup Table"),
                    'selectLabel': gettext("Select a Lookup Table..."),
                    'advancedLabel': gettext("Advanced Lookup Table Options"),
                };
            }
        });

        self.receiverExpression = ko.observable(options.receiverExpression);
        self.itemListOptions = ko.computed(function () {
            var itemLists = get('js_options').item_lists;
            return _.map(
                _.filter(itemLists, function (p) {
                    return p.fixture_type === self.appearance();
                }),
                function (p) {
                    return {
                        "value": p.id,
                        "name": p.name,
                    };
                }
            );
        });
        self.itemset = itemsetModel(options.itemsetOptions, saveButton);

        subscribeToSave(self, [
            'name', 'label', 'hint', 'appearance', 'defaultValue', 'hidden',
            'receiverExpression', 'isMultiselect', 'allowBlankValue', 'exclude',
            'requiredTest', 'requiredText', 'validationTest', 'validationText',
        ], saveButton);
        return self;
    };

    var defaultPropertyModel = function (options, saveButton) {
        options = _.defaults(options, {
            property: '',
            defaultValue: '',
        });
        var self = ko.mapping.fromJS(options);

        subscribeToSave(self, ['property', 'defaultValue'], saveButton);

        return self;
    };

    var additionalRegistryCaseModel = function (xpath, saveButton) {
        var self = {};
        self.uniqueId = generateSemiRandomId();
        self.caseIdXpath = ko.observable(xpath || '');
        subscribeToSave(self, ['caseIdXpath'], saveButton);
        return self;
    };

    var searchConfigKeys = [
        'autoLaunch', 'blacklistedOwnerIdsExpression', 'defaultSearch', 'searchAgainLabel',
        'searchButtonDisplayCondition', 'searchLabel', 'searchFilter',
        'searchAdditionalRelevant', 'dataRegistry', 'dataRegistryWorkflow', 'additionalRegistryCases',
        'customRelatedCaseProperty', 'inlineSearch', 'titleLabel',
    ];
    var searchConfigModel = function (options, lang, searchFilterObservable, saveButton) {
        hqImport("hqwebapp/js/assert_properties").assertRequired(options, searchConfigKeys);

        options.searchLabel = options.searchLabel[lang] || "";
        options.searchAgainLabel = options.searchAgainLabel[lang] || "";
        options.titleLabel = options.titleLabel[lang] || "";
        var mapping = {
            'additionalRegistryCases': {
                create: function(options) {
                    return additionalRegistryCaseModel(options.data, saveButton);
                },
            },
        };
        var self = ko.mapping.fromJS(options, mapping);

        self.restrictWorkflowForDataRegistry = ko.pureComputed(() => {
            return self.dataRegistry() && self.dataRegistryWorkflow() === 'load_case';
        });

        self.workflow = ko.computed({
            read: function () {
                if (self.restrictWorkflowForDataRegistry()) {
                    if (self.autoLaunch()) {
                        if (self.defaultSearch()) {
                            return "es_only";
                        }
                    }
                    return "auto_launch";
                }
                if (self.autoLaunch()) {
                    if (self.defaultSearch()) {
                        return "es_only";
                    }
                    return "auto_launch";
                } else if (self.defaultSearch()) {
                    return "see_more";
                }
                return "classic";
            },
            write: function (value) {
                self.autoLaunch(_.contains(["es_only", "auto_launch"], value));
                self.defaultSearch(_.contains(["es_only", "see_more"], value));
            },
        });

        self.inlineSearchVisible = ko.computed(() => {
            return self.workflow() === "es_only" || self.workflow() === "auto_launch";
        });

        self.inlineSearchActive = ko.computed(() => {
            return self.inlineSearchVisible() && self.inlineSearch();
        });

        // Allow search filter to be copied from another part of the page
        self.setSearchFilterVisible = ko.computed(function () {
            return searchFilterObservable && searchFilterObservable();
        });
        self.setSearchFilterEnabled = ko.computed(function () {
            return self.setSearchFilterVisible() && searchFilterObservable() !== self.searchFilter();
        });
        self.setSearchFilter = function () {
            self.searchFilter(searchFilterObservable());
        };

        subscribeToSave(self, searchConfigKeys, saveButton);
        // media image/audio buttons
        $(".case-search-multimedia-input button").on("click", function () {
            saveButton.fire('change');
        });
        // checkbox to select media for all languages
        $(".case-search-multimedia-input input[type='checkbox']").on('change', function () {
            saveButton.fire('change');
        });

        self.addRegistryQuery = function () {
            self.additionalRegistryCases.push(additionalRegistryCaseModel('', saveButton));
        };

        self.removeRegistryQuery = function (model) {
            self.additionalRegistryCases.remove(model);
        };

        self.serialize = function () {
            return {
                auto_launch: self.autoLaunch(),
                default_search: self.defaultSearch(),
                search_additional_relevant: self.searchAdditionalRelevant(),
                search_button_display_condition: self.searchButtonDisplayCondition(),
                data_registry: self.dataRegistry(),
                data_registry_workflow: self.dataRegistryWorkflow(),
                search_label: self.searchLabel(),
                search_label_image:
                    $("#case_search-search_label_media_media_image input[type=hidden][name='case_search-search_label_media_media_image']").val() || null,
                search_label_image_for_all:
                    $("#case_search-search_label_media_media_image input[type=hidden][name='case_search-search_label_media_use_default_image_for_all']").val() || null,
                search_label_audio:
                    $("#case_search-search_label_media_media_audio input[type=hidden][name='case_search-search_label_media_media_audio']").val() || null,
                search_label_audio_for_all:
                    $("#case_search-search_label_media_media_audio input[type=hidden][name='case_search-search_label_media_use_default_audio_for_all']").val() || null,
                search_again_label: self.searchAgainLabel(),
                search_again_label_image:
                    $("#case_search-search_again_label_media_media_image input[type=hidden][name='case_search-search_again_label_media_media_image']").val() || null,
                search_again_label_image_for_all:
                    $("#case_search-search_again_label_media_media_image input[type=hidden][name='case_search-search_again_label_media_use_default_image_for_all']").val() || null,
                search_again_label_audio:
                    $("#case_search-search_again_label_media_media_audio input[type=hidden][name='case_search-search_again_label_media_media_audio']").val() || null,
                search_again_label_audio_for_all:
                    $("#case_search-search_again_label_media_media_audio input[type=hidden][name='case_search-search_again_label_media_use_default_audio_for_all']").val() || null,
                search_filter: self.searchFilter(),
                title_label: self.titleLabel(),
                blacklisted_owner_ids_expression: self.blacklistedOwnerIdsExpression(),
                additional_registry_cases: self.dataRegistryWorkflow() === "load_case" ?  self.additionalRegistryCases().map((query) => {
                    return query.caseIdXpath();
                }) : [],
                custom_related_case_property: self.customRelatedCaseProperty(),
                inline_search: self.inlineSearch(),
            };
        };

        return self;
    };

    var _getAppearance = function (searchProperty) {
        // init with blank string to avoid triggering save button
        var appearance = searchProperty.appearance || "";
        if (searchProperty.input_ === "select1" || searchProperty.input_ === "select") {
            var uri = searchProperty.itemset.instance_uri;
            if (uri !== null && uri.includes("commcare-reports")) {
                appearance = "report_fixture";
            }
            else {
                appearance = "lookup_table_fixture";
            }
        }
        if (searchProperty.appearance === "address") {
            appearance = "address";
        }
        if (["date", "daterange"].indexOf(searchProperty.input_) !== -1) {
            appearance = searchProperty.input_;
        }
        return appearance;
    };

    var searchViewModel = function (searchProperties, defaultProperties, searchConfigOptions, lang, saveButton, searchFilterObservable) {
        var self = {};

        self.searchConfig = searchConfigModel(searchConfigOptions, lang, searchFilterObservable, saveButton);
        self.defaultProperties = ko.observableArray();

        // searchProperties is a list of CaseSearchProperty objects
        var wrappedSearchProperties = _.map(searchProperties, function (searchProperty) {
            // The model supports multiple validation conditions, but we don't need the UI for it yet
            var validation = searchProperty.validations[0];
            return searchPropertyModel({
                name: searchProperty.name,
                label: searchProperty.label[lang],
                hint: searchProperty.hint[lang],
                appearance: _getAppearance(searchProperty),
                isMultiselect: searchProperty.input_ === "select",
                allowBlankValue: searchProperty.allow_blank_value,
                exclude: searchProperty.exclude,
                requiredTest: searchProperty.required.test,
                requiredText: searchProperty.required.text[lang],
                validationTest: validation ? validation.test : '',
                validationText: validation ? validation.text[lang] : '',
                defaultValue: searchProperty.default_value,
                hidden: searchProperty.hidden,
                receiverExpression: searchProperty.receiver_expression,
                itemsetOptions: {
                    instance_id: searchProperty.itemset.instance_id,
                    instance_uri: searchProperty.itemset.instance_uri,
                    nodeset: searchProperty.itemset.nodeset,
                    label: searchProperty.itemset.label,
                    value: searchProperty.itemset.value,
                    sort: searchProperty.itemset.sort,
                },
            }, saveButton);
        });

        self.searchProperties = ko.observableArray(
            wrappedSearchProperties.length > 0 ? wrappedSearchProperties : [searchPropertyModel({}, saveButton)]
        );

        self.addProperty = function () {
            self.searchProperties.push(searchPropertyModel({}, saveButton));
        };
        self.removeProperty = function (property) {
            self.searchProperties.remove(property);
        };
        self._getProperties = function () {
            // i.e. [{'name': p.name, 'label': p.label} for p in self.searchProperties if p.name]
            return _.map(
                _.filter(
                    self.searchProperties(),
                    function (p) { return p.name().length > 0; }  // Skip properties where name is blank
                ),
                function (p) {
                    var ifNotHidden = function (val) { return p.hidden() ? "" : val; };
                    return {
                        name: p.name(),
                        label: p.label().length ? p.label() : p.name(),  // If label isn't set, use name
                        hint: p.hint(),
                        appearance: p.appearanceFinal(),
                        is_multiselect: p.isMultiselect(),
                        allow_blank_value: p.allowBlankValue(),
                        exclude: p.exclude(),
                        required_test: ifNotHidden(p.requiredTest()),
                        required_text: ifNotHidden(p.requiredText()),
                        validation_test: ifNotHidden(p.validationTest()),
                        validation_text: ifNotHidden(p.validationText()),
                        default_value: p.defaultValue(),
                        hidden: p.hidden(),
                        receiver_expression: p.receiverExpression(),
                        fixture: ko.toJSON(p.itemset),
                    };
                }
            );
        };

        if (defaultProperties.length > 0) {
            for (var k = 0; k < defaultProperties.length; k++) {
                self.defaultProperties.push(defaultPropertyModel({
                    property: defaultProperties[k].property,
                    defaultValue: defaultProperties[k].defaultValue,
                }, saveButton));
            }
        } else {
            self.defaultProperties.push(defaultPropertyModel({}, saveButton));
        }
        self.addDefaultProperty = function () {
            self.defaultProperties.push(defaultPropertyModel({}, saveButton));
        };
        self.removeDefaultProperty = function (property) {
            self.defaultProperties.remove(property);
        };
        self._getDefaultProperties = function () {
            return _.map(
                _.filter(
                    self.defaultProperties(),
                    function (p) { return p.property().length > 0; }  // Skip properties where property is blank
                ),
                function (p) {
                    return {
                        property: p.property(),
                        defaultValue: p.defaultValue(),
                    };
                }
            );
        };

        self.commonProperties = ko.computed(function () {
            var defaultProperties = _.map(self._getDefaultProperties(), function (p) {
                return p.property;
            });
            var commonProperties = self.searchProperties().filter(function (n) {
                return n.name().length > 0 && defaultProperties.indexOf(n.name()) !== -1;
            });
            return _.map(
                commonProperties,
                function (p) {
                    return p.name();
                }
            );
        });

        self.isCommon = function (prop) {
            return self.commonProperties().indexOf(prop) !== -1;
        };

        self.isEnabled = ko.computed(() => {
            // match logic in corehq.apps.app_manager.util.module_offers_search
            return self._getProperties().length > 0 || self._getDefaultProperties().length > 0;
        });

        self.serialize = function () {
            return _.extend({
                properties: self._getProperties(),
                default_properties: self._getDefaultProperties(),
            }, self.searchConfig.serialize());
        };

        subscribeToSave(self, ['searchProperties', 'defaultProperties'], saveButton);

        return self;
    };

    return {
        searchConfigKeys: searchConfigKeys,
        searchViewModel: searchViewModel,
    };
});
