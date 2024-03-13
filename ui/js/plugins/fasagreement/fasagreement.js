//
// FreeIPA plugin for Fedora Account System
// Copyright (C) 2019 FreeIPA FAS Contributors
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
          facet_groups: ['member', 'memberuser', 'settings'],
          facets: [
              {
                  $type: 'search',
                  row_enabled_attribute: 'ipaenabledflag',
                  columns: [
                      'cn',
                      {
                          name: 'ipaenabledflag',
                          label: '@i18n:status.label',
                          formatter: 'boolean_status'
                      },
                      'description'
                  ],
                  actions: [
                      'batch_disable',
                      'batch_enable'
                  ],
                  control_buttons: [
                      {
                          name: 'disable',
                          label: '@i18n:buttons.disable',
                          icon: 'fa-minus'
                      },
                      {
                          name: 'enable',
                          label: '@i18n:buttons.enable',
                          icon: 'fa-check'
                      }
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
                      'enable',
                      'disable',
                      'delete'
                  ],
                  header_actions: ['enable', 'disable', 'delete'],
                  state: {
                      evaluators: [
                          {
                              $factory: IPA.enable_state_evaluator,
                              field: 'ipaenabledflag'
                          }
                      ],
                      summary_conditions: [
                          IPA.enabled_summary_cond,
                          IPA.disabled_summary_cond
                      ]
                  }
              },
              {
                  $type: 'association',
                  name: 'member_group',
                  add_method: 'add_group',
                  remove_method: 'remove_group'
              },
              {
                  $type: 'association',
                  name: 'memberuser_user',
                  columns: [
                      'uid',
                      'uidnumber',
                      'mail'
                  ],
                  adder_columns: [
                      {
                          name: 'uid',
                          primary_key: true
                      }
                  ],
                  add_method: 'add_user',
                  remove_method: 'remove_user'
              }
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
      var identity_item = menu.query({name: 'identity'});
      if (identity_item.length > 0) {
          menu.add_item(exp.fasagreement_menu_spec, 'identity');
      }
  };

  phases.on('registration', exp.register);
  phases.on('profile', exp.add_menu_item, 20);

  return exp;
});