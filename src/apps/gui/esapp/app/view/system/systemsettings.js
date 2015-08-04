
Ext.define("esapp.view.system.systemsettings",{
    "extend": "Ext.form.Panel",
    "controller": "system-systemsettings",
    "viewModel": {
        "type": "system-systemsettings"
    },

    xtype  : 'systemsettings',
    name :  'systemsettings',
    id: 'systemsettingsview',

    requires: [
        'esapp.view.system.systemsettingsController',
        'esapp.view.system.systemsettingsModel',
        'esapp.view.system.PCModeAdmin',
        'esapp.view.system.PCVersionAdmin',
        'esapp.view.system.ThemaAdmin',
        'esapp.view.system.PCLogLevelAdmin',
        'esapp.view.system.IPAddressAdmin',

        'Ext.form.FieldSet',
        'Ext.form.field.Number',
        'Ext.tip.ToolTip'
    ],

//    store: 'SystemSettingsStore',
//    bind:'{system_setting}',
    session:true,

    title: '', // 'System settings',
    titleAlign: 'center',
    border:true,
    frame:true,
    width:800,
    autoScroll:false,
    fieldDefaults: {
        labelWidth: 120,
        labelAlign: 'left'
    },
    bodyPadding:'5 0 5 15',
    viewConfig:{forceFit:true},
    layout:'hbox',

    fieldset_title_database_connection_settings : '<b>Database connection settings</b>',   // EMMA.getTranslation('fieldset_title_database_connection_settings'),
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
    form_fieldlabel_get_internet_output_dir     : 'Get Eumetcast output directory',
    form_fieldlabel_get_eumetcast_output_dir    : 'Get Internet output directory',

    fieldset_title_system_settings              : '<b>System settings</b>',
    form_fieldlabel_ip_pc1                      : 'PC1',
    form_fieldlabel_ip_pc2                      : 'PC2',
    form_fieldlabel_ip_pc3                      : 'PC3',
    form_fieldlabel_current_mode                : 'Current mode',
    form_fieldlabel_active_verion               : 'Active version',
    form_fieldlabel_type_of_install             : 'Type of Install',
    form_fieldlabel_role                        : 'Role',
    form_fieldlabel_thema                       : 'Thema',
    form_fieldlabel_loglevel                    : 'Log level',

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
        me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('systemsettings') + '</span>');

        var ip_pc1 = {
            items:[{
                id: 'ip_pc1',
                name: 'ip_pc1',
                bind: '{system_setting.ip_pc1}',
                xtype: 'displayfield',
                fieldLabel: me.form_fieldlabel_ip_pc1,
                vtype: 'IPAddress',
                msgTarget: 'side',
                fieldStyle:'font-weight: bold;',
                allowBlank: false,
                flex: 2.2
            }]
        };

        var ip_pc2 = {
            items:[{
                id: 'ip_pc2',
                name: 'ip_pc2',
                bind: '{system_setting.ip_pc2}',
                xtype: 'displayfield',
                fieldLabel: me.form_fieldlabel_ip_pc2,
                vtype: 'IPAddress',
                msgTarget: 'side',
                fieldStyle:'font-weight: bold;',
                allowBlank: false,
                flex: 2.2
            }]
        };
        var ip_pc3 = {
            items:[{
                id: 'ip_pc3',
                name: 'ip_pc3',
                bind: '{system_setting.ip_pc3}',
                xtype: 'displayfield',
                fieldLabel: me.form_fieldlabel_ip_pc3,
                vtype: 'IPAddress',
                msgTarget: 'side',
                fieldStyle:'font-weight: bold;',
                allowBlank: false,
                flex: 2.2
            }]
        };

        var modify_ips_btn = {
            xtype: 'button',
            text: 'Modify',
            align:'right',
            flex: 0.8,
            iconCls: 'fa fa-pencil-square-o',
            style: { color: 'white' },
            // glyph: 'xf055@FontAwesome',
            //scale: 'medium',
            scope:me,
            handler: function(){
                var IPAdminWin = new esapp.view.system.IPAddressAdmin({
                    params: {}
                });
                IPAdminWin.show();
            }
        };

        var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
        var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
            scope: me,
            failure: function(record, operation) {
                //console.info('failure');
            },
            success: function(record, operation) {
                me.type_install = record.data.type_installation

                var ipadresses_fieldset = Ext.getCmp('ipaddresses');
                if (me.type_install == 'Full'){
                    ipadresses_fieldset.add(ip_pc1);
                    ipadresses_fieldset.add(ip_pc2);
                    ip_pc3.items.push(modify_ips_btn);
                    ipadresses_fieldset.add(ip_pc3);
                }
                else {
                    ipadresses_fieldset.add(ip_pc1);
                    ip_pc2.items.push(modify_ips_btn);
                    ipadresses_fieldset.add(ip_pc2);
                }
            }
        });

        me.dockedItems=  [{
            dock: 'bottom',
            xtype: 'toolbar',
            items : [{
                text: 'Create System Report',
                scope: me,
                iconCls: 'fa fa-download fa-2x',
                style: { color: 'blue' },
                scale: 'medium',
                disabled: false,
                handler: function () {
                    if (!Ext.fly('frmExportDummy')) {
                        var frm = document.createElement('form');
                        frm.id = 'frmExportDummy';
                        frm.name = id;
                        frm.className = 'x-hidden';
                        document.body.appendChild(frm);
                    }

                    Ext.Ajax.request({
                        method: 'POST',
                        url: 'systemsettings/systemreport',
                        isUpload: true,
                        form: Ext.fly('frmExportDummy'),
                        success: function(response, opts){
                            //var result = Ext.JSON.decode(response.responseText);
                            //if (result.success){
                            //    Ext.toast({ html: 'Download system report', title: 'System report', width: 200, align: 't' });
                            //}
                        },
                        failure: function(response, opts) {
                            console.info(response.status);
                        }
                    });
                }
            },{
                text: 'Create Install Report',
                scope:me,
                iconCls: 'fa fa-download fa-2x',
                style: { color: 'blue' },
                scale: 'medium',
                disabled: false,
                handler: function(){
                    if (!Ext.fly('frmExportDummy')) {
                        var frm = document.createElement('form');
                        frm.id = 'frmExportDummy';
                        frm.name = id;
                        frm.className = 'x-hidden';
                        document.body.appendChild(frm);
                    }
                   Ext.Ajax.request({
                        method: 'GET',
                        url: 'systemsettings/installreport',
                        isUpload: true,
                        form: Ext.fly('frmExportDummy'),
                        success: function(response, opts){
                            //var result = Ext.JSON.decode(response.responseText);
                            //if (result.success){
                            //    Ext.toast({ html: 'Download install report', title: 'Install report', width: 200, align: 't' });
                            //}
                        },
                        failure: function(response, opts) {
                            console.info(response.status);
                        }
                    });
                }
            },'->',{
                text: 'Reset to factory settings',
                scope:me,
                iconCls: 'fa fa-undo fa-2x',    // 'apply_globals-icon',
                style: { color: 'orange' },
                scale: 'medium',
                disabled: false,
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
            },{
                text: 'Save',
                scope:me,
                iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
                style: { color: 'lightblue' },
                scale: 'medium',
                disabled: false,
                handler: function(){
                    // me.onHandleAction('Save','save');
                    if (me.getSession().getChanges() != null){
                        me.getSession().getSaveBatch().start();
                        Ext.toast({ html: 'System Settings are saved!', title: 'System settings saved', width: 200, align: 't' });
                    }
                }
            }]
        }];

        me.items = [{
            margin:'0 15 5 0',
            items: [{
                xtype: 'fieldset',
                title: me.fieldset_title_system_settings,
                collapseable:false,
                height:'800',
                defaults: {
                    width: 350,
                    labelWidth: 100
                },
                items: [{
                    xtype: 'fieldset',
                    title: '',
                    collapseable:false,
                    padding: 5,
                    defaults: {
                        labelWidth: 100
                    },
                    items:[{
                       id: 'type_of_install',
                       name: 'type_of_install',
                       bind: '{system_setting.type_installation}',
                       xtype: 'displayfield',
                       fieldLabel: me.form_fieldlabel_type_of_install,
                       fieldStyle:'font-weight: bold;'
                    },{
                       id: 'role',
                       name: 'role',
                       bind: '{system_setting.role}',
                       xtype: 'displayfield',
                       fieldLabel: me.form_fieldlabel_role,
                       fieldStyle:'font-weight: bold;'
                    }]
                },{
                    xtype: 'fieldset',
                    title: '',
                    collapseable:false,
                    padding: 10,
                    defaults: {
                        labelWidth: 100,
                        layout: 'hbox'
                    },
                    items:[{
                       items:[{
                           id: 'current_mode',
                           name: 'current_mode',
                           bind: '{system_setting.current_mode}',
                           xtype: 'displayfield',
                           fieldLabel: me.form_fieldlabel_current_mode,
                           fieldStyle:'font-weight: bold;',
                           flex: 2.2
                        },{
                            xtype: 'button',
                            text: 'Modify',
                            flex: 0.8,
                            iconCls: 'fa fa-pencil-square-o',
                            style: { color: 'white' },
                            // glyph: 'xf055@FontAwesome',
                            //scale: 'medium',
                            scope:me,
                            handler: function(){
                                var PCModeAdminWin = new esapp.view.system.PCModeAdmin({
                                    params: {
                                        currentmode: Ext.getCmp('current_mode').getValue()
                                    }
                                });
                                PCModeAdminWin.show();
                            }
                        }]
                    },{
                       items:[{
                           id: 'active_version',
                           name: 'active_version',
                           bind: '{system_setting.active_version}',
                           xtype: 'displayfield',
                           fieldLabel: me.form_fieldlabel_active_verion,
                           fieldStyle:'font-weight: bold;',
                           flex: 2.2
                        },{
                            xtype: 'button',
                            text: 'Modify',
                            flex: 0.8,
                            iconCls: 'fa fa-pencil-square-o',
                            style: { color: 'white' },
                            //scale: 'medium',
                            scope:me,
                            handler: function(){
                                var PCVersionAdminWin = new esapp.view.system.PCVersionAdmin({
                                    params: {
                                        currentversion: Ext.getCmp('active_version').getValue()
                                    }
                                });
                                PCVersionAdminWin.show();
                            }
                        }]
                    },{
                       items:[{
                           id: 'thema',
                           name: 'thema',
                           bind: '{system_setting.thema}',
                           xtype: 'displayfield',
                           fieldLabel: me.form_fieldlabel_thema,
                           fieldStyle:'font-weight: bold;',
                           flex: 2.2
                        },{
                            xtype: 'button',
                            text: 'Modify',
                            flex: 0.8,
                            iconCls: 'fa fa-pencil-square-o',
                            style: { color: 'white' },
                            //scale: 'medium',
                            scope:me,
                            handler: function(){
                                var ThemaAdminWin = new esapp.view.system.ThemaAdmin({
                                    params: {
                                        currentthema: Ext.getCmp('thema').getValue()
                                    }
                                });
                                ThemaAdminWin.show();
                            }
                        }]
                    },{
                       items:[{
                           id: 'loglevel',
                           name: 'loglevel',
                           bind: '{system_setting.loglevel}',
                           xtype: 'displayfield',
                           fieldLabel: me.form_fieldlabel_loglevel,
                           fieldStyle:'font-weight: bold;',
                           flex: 2.2
                        },{
                            xtype: 'button',
                            text: 'Modify',
                            flex: 0.8,
                            iconCls: 'fa fa-pencil-square-o',
                            style: { color: 'white' },
                            //scale: 'medium',
                            scope:me,
                            handler: function(){
                                var LogLevelAdminWin = new esapp.view.system.PCLogLevelAdmin({
                                    params: {
                                        currentloglevel: Ext.getCmp('loglevel').getValue()
                                    }
                                });
                                LogLevelAdminWin.show();
                            }
                        }]
                    }]
                },{
                    xtype: 'fieldset',
                    title: '<b>IP addresses</b>',
                    id: 'ipaddresses',
                    name: 'ipaddresses',
                    collapseable:false,
                    padding: 10,
                    defaults: {
                        labelWidth: 100,
                        layout: 'hbox'
                    }
                }]
            }]
        },{
            items: [{
                xtype: 'fieldset',
                title: me.fieldset_title_path_settings,
                collapseable:false,
                defaults: {
                    width: 350,
                    labelWidth: 120
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
                },{
                   id: 'get_eumetcast_output_dir',
                   name: 'get_eumetcast_output_dir',
                   bind: '{system_setting.get_eumetcast_output_dir}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_get_eumetcast_output_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                },{
                   id: 'get_internet_output_dir',
                   name: 'get_internet_output_dir',
                   bind: '{system_setting.get_internet_output_dir}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_get_internet_output_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                }]
            },{
                xtype: 'fieldset',
                title: me.fieldset_title_database_connection_settings,
                collapseable:false,
                defaults: {
                    width: 350,
                    labelWidth: 120
                },
                items:[{
                   id: 'dbhost',
                   name: 'dbhost',
                   bind: '{system_setting.host}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_dbhost,
                   style:'font-weight: bold;',
                   allowBlank: false,
                   disabled: true
                },{
                   id: 'dbport',
                   name: 'dbport',
                   bind: '{system_setting.port}',
                   xtype: 'numberfield',
                   fieldLabel: me.form_fieldlabel_dbport,
                   style:'font-weight: bold;',
                   width: 250,
                   allowBlank: false,
                   disabled: true
                },{
                   id: 'dbuser',
                   name: 'dbuser',
                   bind: '{system_setting.dbuser}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_dbuser,
                   style:'font-weight: bold;',
                   allowBlank: false,
                   disabled: true
                },{
                   id: 'dbpassword',
                   name: 'dbpassword',
                   bind: '{system_setting.dbpass}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_dbpassword,
                   style:'font-weight: bold;',
                   allowBlank: false,
                   disabled: true
                },{
                   id: 'dbname',
                   name: 'dbname',
                   bind: '{system_setting.dbname}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_dbname,
                   style:'font-weight: bold;',
                   allowBlank: false,
                   disabled: true
                }]
            }]
        }];

        me.callParent();
    }

});
