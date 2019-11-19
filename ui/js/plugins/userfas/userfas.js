//
// FreeIPA plugin for Fedora Account System
// Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
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
                    name: 'fastimezone',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'faslocale',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasircnick',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fastimezone',
                    flags: ['w_if_no_aci']
                }, {
                    $type: 'multivalued',
                    name: 'fasgpgkeyid',
                    flags: ['w_if_no_aci']
                }, {
                    $type: 'datetime',
                    name: 'fascreationtime',
                    read_only: true
                }, {
                    name: 'fasstatusnote',
                    flags: ['w_if_no_aci']
                }]
            };
            var facet = get_item(IPA.user.entity_spec.facets, '$type', 'details');
            facet.sections.push(section);
            return true;
        };

        phases.on('customization', userfas_plugin.add_user_fas_pre_op);

        return userfas_plugin;
    });
