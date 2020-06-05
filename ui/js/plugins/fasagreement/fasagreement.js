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

        var exp = IPA.fasagreement = {};

        var make_spec = function () {
            var spec = {
                name: 'fasagreement',
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
                    title: '@i18n:fasagreement.add',
                    fields: [
                        'cn',
                        {
                            $type: 'textarea',
                            name: 'description'
                        }
                    ]
                },
                deleter_dialog: {
                    title: '@i18n:fasagreement.remove'
                }
            };
            return spec;
        };

        exp.entity_spec = make_spec();

        exp.fasagreement_menu_spec = {
            entity: 'fasagreement',
            label: '@i18n:fasagreement.fasagreements'
        };

        exp.register = function () {
            var e = reg.entity;
            e.register({type: 'fasagreement', spec: exp.entity_spec});
        };

        exp.add_menu_item = function () {
            menu.add_item(exp.fasagreement_menu_spec, 'identity');
        };

        phases.on('registration', exp.register);
        phases.on('profile', exp.add_menu_item, 20);

        return exp;
    });
