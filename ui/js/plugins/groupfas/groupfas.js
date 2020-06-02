//
// FreeIPA plugin for Fedora Account System
// Copyright (C) 2020  FAS Contributors
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

        groupfas_plugin.add_group_fas_pre_op = function() {
            var section = {
                name: 'groupfas',
                label: '@i18n:groupfas.name',
                fields: [{
                    name: 'fasgroup',
                    $type: 'checkbox',
                    flags: ['w_if_no_aci']
                },{
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

        groupfas_plugin.add_search_group_fas = function() {
            var fasgroup = {
                name: 'fasgroup',
                label: '@i18n:groupfas.group',
                formatter: 'boolean_status'
            };
            var facet = get_item(IPA.group.entity_spec.facets, '$type', 'search');
            facet['columns'].splice(1, 0, fasgroup);
            return true;
        };

        phases.on('customization', groupfas_plugin.add_group_fas_pre_op);
        phases.on('customization', groupfas_plugin.add_search_group_fas);

        return groupfas_plugin;
    });
