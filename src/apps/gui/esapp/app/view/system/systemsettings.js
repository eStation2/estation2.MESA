
Ext.define("esapp.view.system.systemsettings",{
    "extend": "Ext.form.Panel",
    "controller": "system-systemsettings",
    "viewModel": {
        "type": "system-systemsettings"
    },

    xtype  : 'systemsettings',
    name :  'systemsettings',

    requires: [
        'esapp.view.system.systemsettingsController',
        'esapp.view.system.systemsettingsModel',
        'Ext.form.FieldSet',
        'Ext.form.field.Number'
    ],

//    store: 'SystemSettingsStore',
//    bind:'{system_setting}',
    session:true,

    title: 'System settings',
    border:true,
    frame:true,
    width:650,
    autoScroll:false,
    fieldDefaults: {
        labelWidth: 160,
        labelAlign: 'left'
    },
    bodyPadding:10,
    viewConfig:{forceFit:true},
    layout:'form',

    fieldset_title_database_connestion_settings : '<b>Database connection settings</b>',   // EMMA.getTranslation('fieldset_title_database_connestion_settings'),
    form_fieldlabel_dbhost                      : 'Host',
    form_fieldlabel_dbport                      : 'Port',
    form_fieldlabel_dbuser                      : 'User name',
    form_fieldlabel_dbpassword                  : 'Password',
    form_fieldlabel_dbname                      : 'Database name',

    fieldset_title_path_settings                : '<b>Path settings</b>',
    form_fieldlabel_base_dir                    : 'Base directory',
    form_fieldlabel_base_tmp_dir                : 'Base temporary directory',
    form_fieldlabel_data_dir                    : 'Data directory',
    form_fieldlabel_ingest_dir                  : 'Ingest directory',
    form_fieldlabel_static_data_dir             : 'Static data directory',
    form_fieldlabel_archive_dir                 : 'Archive directory',
    form_fieldlabel_eumetcast_files_dir         : 'Eumetcast files directory',
    //form_fieldlabel_ingest_server_in_dir        : 'Ingest server in directory',

    tools: [
    {
        type: 'refresh',
        tooltip: 'Reload system parameters.',
        callback: function (formpanel) {
            var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
            var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
                scope: formpanel,
                failure: function(record, operation) {
                    //console.info('failure');
                },
                success: function(record, operation) {
                    formpanel.loadRecord(systemsettingsrecord);
                    formpanel.updateRecord();
                }
            });
        }
    }],

    initComponent: function () {
        var me = this;

        me.tbar =[{
            text: 'Save',
            iconCls: 'icon-disk',
            scope:me,
            handler: function(){
                // me.onHandleAction('Save','save');
                if (me.getSession().getChanges() != null){
                    me.getSession().getSaveBatch().start();
                    Ext.toast({ html: 'System Settings are saved!', title: 'System settings saved', width: 200, align: 't' });
                }
            }
        },'->',{
            text: 'Reset to factory settings',
            iconCls: 'apply_globals-icon',
            scope:me,
            handler: function(){
                // me.onHandleAction('Reset','reset');
               Ext.Ajax.request({
                    method: 'GET',
                    url: 'systemsettings/reset',
                    success: function(response, opts){
                        var result = Ext.JSON.decode(response.responseText);
                        if (result.success){
                            Ext.toast({ html: 'Settings are reseted to factory settings', title: 'Reset to factory settings', width: 200, align: 't' });
                        }
                        var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
                        var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
                            scope: me,
                            failure: function(record, operation) {
                                //console.info('failure');
                            },
                            success: function(record, operation) {
                                me.loadRecord(systemsettingsrecord);
                                me.updateRecord();
                            }
                        });
                    },
                    failure: function(response, opts) {
                        console.info(response.status);
                    }
                });
            }
        }];

        me.items = [{
            xtype: 'fieldset',
            title: me.fieldset_title_path_settings,
            collapseable:false,
            defaults: {
                width: 550,
                labelWidth: 160
            },
            items:[{
               id: 'base_dir',
               name: 'base_dir',
               bind: '{system_setting.base_dir}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_base_dir,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'base_tmp_dir',
               name: 'base_tmp_dir',
               bind: '{system_setting.base_tmp_dir}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_base_tmp_dir,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'data_dir',
               name: 'data_dir',
               bind: '{system_setting.data_dir}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_data_dir,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'ingest_dir',
               name: 'ingest_dir',
               bind: '{system_setting.ingest_dir}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_ingest_dir,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'static_data_dir',
               name: 'static_data_dir',
               bind: '{system_setting.static_data_dir}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_static_data_dir,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'archive_dir',
               name: 'archive_dir',
               bind: '{system_setting.archive_dir}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_archive_dir,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'eumetcast_files_dir',
               name: 'eumetcast_files_dir',
               bind: '{system_setting.eumetcast_files_dir}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_eumetcast_files_dir,
               style:'font-weight: bold;',
               allowBlank: false
            //},{
            //   id: 'ingest_server_in_dir',
            //   name: 'ingest_server_in_dir',
            //   bind: '{system_setting.ingest_server_in_dir}',
            //   xtype: 'textfield',
            //   fieldLabel: me.form_fieldlabel_ingest_server_in_dir,
            //   style:'font-weight: bold;',
            //   allowBlank: false
            }]
        },{
            xtype: 'fieldset',
            title: me.fieldset_title_database_connestion_settings,
            collapseable:false,
            defaults: {
                width: 350,
                labelWidth: 160
            },
            items:[{
               id: 'dbhost',
               name: 'dbhost',
               bind: '{system_setting.host}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_dbhost,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'dbport',
               name: 'dbport',
               bind: '{system_setting.port}',
               xtype: 'numberfield',
               fieldLabel: me.form_fieldlabel_dbport,
               style:'font-weight: bold;',
               width: 250,
               allowBlank: false
            },{
               id: 'dbuser',
               name: 'dbuser',
               bind: '{system_setting.dbuser}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_dbuser,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'dbpassword',
               name: 'dbpassword',
               bind: '{system_setting.dbpass}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_dbpassword,
               style:'font-weight: bold;',
               allowBlank: false
            },{
               id: 'dbname',
               name: 'dbname',
               bind: '{system_setting.dbname}',
               xtype: 'textfield',
               fieldLabel: me.form_fieldlabel_dbname,
               style:'font-weight: bold;',
               allowBlank: false
            }]
        }];

        me.callParent();
    }

});
