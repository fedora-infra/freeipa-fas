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

        var groupfas_plugin = {};

        groupfas_plugin.add_user_fas_pre_op = function() {
            var section = {
                name: 'groupfas',
                label: '@i18n:groupfas.name',
                fields: [{
                    name: 'fasurl',
                    $type: 'multivalued',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasmailinglist',
                    flags: ['w_if_no_aci']
                }, {
                    name: 'fasircchannel',
                    flags: ['w_if_no_aci']
                }]
            };
            var facet = get_item(IPA.group.entity_spec.facets, '$type', 'details');
            facet.sections.push(section);
            return true;
        };

        phases.on('customization', groupfas_plugin.add_user_fas_pre_op);

        return groupfas_plugin;
    });
