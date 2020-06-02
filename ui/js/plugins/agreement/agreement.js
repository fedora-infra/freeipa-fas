//
// FreeIPA plugin for Fedora Account System
// Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
// See COPYING for license
//

define([
        'freeipa/phases',
        'freeipa/ipa',
        'freeipa/menu',
        'freeipa/reg'
    ],
    function (phases, IPA, menu, reg) {

        var exp = IPA.agreement = {};

        var make_spec = function () {
            var spec = {
                name: 'agreement',
                facets: [
                    {
                        $type: 'search',
                        columns: [
                            "cn"
                        ]
                    },
                    {
                        $type: 'details',
                        sections: [
                            {
                                name: 'details',
                                fields: [
                                    'cn',
                                    {
                                        $type: 'textarea',
                                        name: 'description'
                                    }
                                ]
                            }
                        ],
                        actions: [
                            'select',
                            'delete'
                        ],
                        header_actions: ['delete'],
                        state: {
                            evaluators: [
                                IPA.object_class_evaluator
                            ]
                        }
                    }
                    // TODO: memberuser_user facet
                ],
                standard_association_facets: true,
                adder_dialog: {
                    title: 'Add agreement',
                    fields: [
                        'cn',
                        {
                            $type: 'textarea',
                            name: 'description'
                        }
                    ]
                },
                deleter_dialog: {
                    title: 'Remove Agreement'
                }
            };
            return spec;
        };

        exp.entity_spec = make_spec();

        exp.agreement_menu_spec = {
            entity: 'agreement',
            label: '@i18n:agreement.agreements'
        };

        exp.register = function () {
            var e = reg.entity;
            e.register({type: 'agreement', spec: exp.entity_spec});
        };

        exp.add_menu_item = function () {
            menu.add_item(exp.agreement_menu_spec, 'identity');
        };

        phases.on('registration', exp.register);
        phases.on('profile', exp.add_menu_item, 20);

        return exp;
    });
