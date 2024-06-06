//
// FreeIPA plugin for Fedora Account System
// Copyright (C) 2019  FreeIPA FAS Contributors
// See COPYING for license
//

define([
        'freeipa/phases',
        'freeipa/ipa'
    ],
    function(phases, IPA) {

        // helper function
        function get_item(array, attr, value) {

            for (var i = 0, l = array.length; i < l; i++) {
                if (array[i][attr] === value) return array[i];
            }
            return null;
        }

        var userfas_plugin = {};

        userfas_plugin.add_user_fas_pre_op = function() {
            var section = {
                name: 'userfas',
                label: '@i18n:userfas.name',
                fields: [{
                    name: 'fastimezone',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'faslocale',
                    flags: ['w_if_no_aci']
                }, {
                    $type: 'multivalued',
                    name: 'fasircnick',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fastimezone',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'faswebsiteurl',
                    $type: 'multivalued',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasrhbzemail',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasgithubusername',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasgitlabusername',
                    flags: ['w_if_no_aci']
                }, {
                    $type: 'multivalued',
                    name: 'fasgpgkeyid',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasisprivate',
                    $type: 'checkbox',
                    flags: ['w_if_no_aci']
                }, {
                    $type: 'datetime',
                    name: 'fascreationtime',
                    read_only: true
                }, {
                    name: 'fasstatusnote',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'faspronoun',
                    $type: 'multivalued',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasrssurl',
                    $type: 'multivalued',
                    flags: ['w_if_no_aci']
                }]
            };
            var fasagreement = {
                $type: 'association',
                $pre_ops: [IPA.user.association_facet_ss_pre_op],
                name: 'memberof_fasagreement',
                associator: IPA.serial_associator,
                add_method: 'add_user',
                add_title: '@i18n:fasagreement.add',
                remove_method: 'remove_user',
                remove_title: '@i18n:fasagreement.remove'
            };
            [IPA.user.entity_spec, IPA.stageuser.stageuser_spec].forEach(function(spec) {
              var facet = get_item(spec.facets, '$type', 'details');
              facet.sections.push(section);

              spec.facets.push(fasagreement);
            });
            return true;
        };

        phases.on('customization', userfas_plugin.add_user_fas_pre_op);

        return userfas_plugin;
    });
