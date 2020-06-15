//
// FreeIPA plugin for Fedora Account System
// Copyright (C) 2020  FAS Contributors
// See COPYING for license
//

define([
        'freeipa/phases',
        'freeipa/ipa',
        'freeipa/reg'
    ],
    function(phases, IPA, reg) {

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
                label: '@i18n:groupfas.section',
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
            var fasagreement = {
                $type: 'association',
                name: 'memberof_fasagreement',
                associator: IPA.serial_associator,
                add_method: 'add_group',
                add_title: '@i18n:fasagreement.add',
                remove_method: 'remove_group',
                remove_title: '@i18n:fasagreement.remove'
            };

            var facet = get_item(IPA.group.entity_spec.facets, '$type', 'details');
            // Add the details sections
            facet.sections.push(section);
            // Add the make_fasgroup action
            facet.actions.push('make_fasgroup');
            facet.header_actions.splice(-1, 0, 'make_fasgroup');

            // Add user agreement add/remove facet
            IPA.group.entity_spec.facets.push(fasagreement);

            /*
             * Now the add dialog
             */
            // Add the fasgroup checkbox on the adder dialog
            IPA.group.entity_spec.adder_dialog.fields.push({
                $type: 'checkbox',
                name: 'fasgroup'
            });
            // Override the dialog factory to use the checkbox's data
            IPA.fasgroup_adder_dialog = function(spec) {
                var that = IPA.group_adder_dialog(spec);
                var super_create_command = that.create_add_command;
                that.create_add_command = function(record) {
                    var command = super_create_command(record);
                    // If the ckeckbox is checked, add the fasgroup command option
                    var fasgroup_field = that.fields.get_field('fasgroup');
                    var fasgroup = fasgroup_field.save()[0];
                    if (fasgroup) {
                        command.set_option("fasgroup", true);
                    }
                    return command;
                };
                return that;
            }
            IPA.group.entity_spec.adder_dialog["$factory"] = IPA.fasgroup_adder_dialog;

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

        function make_fasgroup_action(spec) {
            spec = spec || {};
            spec.name = spec.name || 'make_fasgroup';
            spec.method = spec.method || 'mod';
            spec.label = spec.label || '@i18n:groupfas.make_fasgroup';
            spec.needs_confirm = spec.needs_confirm !== undefined ? spec.needs_confirm : true;
            spec.disable_cond = spec.disable_cond || ['oc_fasgroup'];
            spec.options = spec.options || {
                fasgroup: true
            };

            var that = IPA.object_action(spec);

            return that;
        }

        phases.on('registration', function() {
            reg.action.register('make_fasgroup', make_fasgroup_action);
        });

        return groupfas_plugin;
    });
