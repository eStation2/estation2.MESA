
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
        //'esapp.view.system.PCRoleAdmin',
        //'esapp.view.system.PCModeAdmin',
        //'esapp.view.system.PCVersionAdmin',
        //'esapp.view.system.ThemaAdmin',
        //'esapp.view.system.PCLogLevelAdmin',
        //'esapp.view.system.IPAddressAdmin',

        'Ext.form.FieldSet',
        'Ext.form.field.Number',
        'Ext.tip.ToolTip'
    ],

    session:true,

    title: '', // 'System settings',
    titleAlign: 'center',
    border:true,
    frame:true,
    //width:850,
    autoWidth: true,
    autoScroll:false,
    fieldDefaults: {
        labelWidth: 120,
        labelAlign: 'left'
    },
    bodyPadding:'5 15 5 15',
    viewConfig:{forceFit:true},
    layout:'hbox',


    initComponent: function () {
        var me = this;
        me.session = true;
        me.setTitle('<span class="panel-title-style">' + esapp.Utils.getTranslation('systemsettings') + '</span>');

        me.fieldset_title_database_connection_settings = '<b>'+esapp.Utils.getTranslation('dbconnectionsettings')+'</b>';
        me.form_fieldlabel_dbhost                      = esapp.Utils.getTranslation('host');   // 'Host';
        me.form_fieldlabel_dbport                      = esapp.Utils.getTranslation('port');   // 'Port';
        me.form_fieldlabel_dbuser                      = esapp.Utils.getTranslation('username');   // 'User name';
        me.form_fieldlabel_dbpassword                  = esapp.Utils.getTranslation('password');   // 'Password';
        me.form_fieldlabel_dbname                      = esapp.Utils.getTranslation('databasename');   // 'Database name';

        me.fieldset_title_path_settings                = '<b>'+esapp.Utils.getTranslation('directorypaths')+'</b>';
        me.form_fieldlabel_base_dir                    = esapp.Utils.getTranslation('basedir');   // 'Base directory';
        me.form_fieldlabel_base_tmp_dir                = esapp.Utils.getTranslation('basetmpdir');   // 'Base temporary directory';
        me.form_fieldlabel_data_dir                    = esapp.Utils.getTranslation('datadir');   // 'Data directory';
        me.form_fieldlabel_ingest_dir                  = esapp.Utils.getTranslation('ingestdir');   // 'Ingest directory';
        me.form_fieldlabel_static_data_dir             = esapp.Utils.getTranslation('staticdatadir');   // 'Static data directory';
        me.form_fieldlabel_archive_dir                 = esapp.Utils.getTranslation('archivedir');   // 'Archive directory';
        me.form_fieldlabel_eumetcast_files_dir         = esapp.Utils.getTranslation('eumetcastfilesdir');   // 'Eumetcast files directory';
        //me.form_fieldlabel_ingest_server_in_dir        = esapp.Utils.getTranslation('ingestserverindir');   // 'Ingest server in directory';
        me.form_fieldlabel_get_internet_output_dir     = esapp.Utils.getTranslation('getinternetoutputdir');   // 'Get Eumetcast output directory';
        me.form_fieldlabel_get_eumetcast_output_dir    = esapp.Utils.getTranslation('geteumetcastoutputdir');   // 'Get Internet output directory';

        me.fieldset_title_system_settings              = '<b>'+esapp.Utils.getTranslation('systemsettings')+'</b>';
        me.form_fieldlabel_ip_pc1                      = esapp.Utils.getTranslation('pc1');   // 'PC1';
        me.form_fieldlabel_ip_pc2                      = esapp.Utils.getTranslation('pc2');   // 'PC2';
        me.form_fieldlabel_ip_pc3                      = esapp.Utils.getTranslation('pc3');   // 'PC3';
        me.form_fieldlabel_current_mode                = esapp.Utils.getTranslation('currentmode');   // 'Current mode';
        me.form_fieldlabel_active_verion               = esapp.Utils.getTranslation('activeversion');   // 'Active version';
        me.form_fieldlabel_type_of_install             = esapp.Utils.getTranslation('typeofinstall');   // 'Type of Install';
        me.form_fieldlabel_role                        = esapp.Utils.getTranslation('role');   // 'Role';
        me.form_fieldlabel_thema                       = esapp.Utils.getTranslation('thema');   // 'Thema';
        me.form_fieldlabel_loglevel                    = esapp.Utils.getTranslation('loglevel');   // 'Log level';
        me.fieldset_title_ipaddresses                  = '<b>'+esapp.Utils.getTranslation('ipaddresses')+'</b>';  // '<b>IP addresses</b>';
        me.fieldset_title_proxy_settings               = '<b>'+esapp.Utils.getTranslation('proxy_settings')+'</b>';   // 'Internet proxy settings';
        me.form_fieldlabel_proxy_host                  = esapp.Utils.getTranslation('proxy_host');   // 'Proxy host';
        me.form_fieldlabel_proxy_port                  = esapp.Utils.getTranslation('proxy_port');   // 'Proxy port';
        me.form_fieldlabel_proxy_user                  = esapp.Utils.getTranslation('proxy_user');   // 'Proxy user';
        me.form_fieldlabel_proxy_userpwd               = esapp.Utils.getTranslation('proxy_userpwd');   // 'Proxy user password';

        var hiddenForWindowsVersion = false;
        if (esapp.globals['typeinstallation'] === 'windows'){
            hiddenForWindowsVersion = true;
        }

        me.tools = [
        {
            type: 'refresh',
            tooltip: esapp.Utils.getTranslation('reloadsystemparams'),   // 'Reload system parameters.',
            callback: function (formpanel) {
                var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
                var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
                    scope: formpanel,
                    loadmask: true,
                    failure: function(record, operation) {
                        //console.info('failure');
                    },
                    success: function(record, operation) {
                        if (operation.success){
                            formpanel.loadRecord(systemsettingsrecord);
                            formpanel.updateRecord();

                            // IN WINDOWS VERSION THEMA MUST BE CHANGEABLE!
                            if (esapp.globals['typeinstallation'] === 'windows'){
                                Ext.getCmp('modify-thema-btn').show();
                            }
                            else {
                                if (record.data.thema != ''){
                                    Ext.getCmp('modify-thema-btn').hide();
                                }
                                else {
                                    Ext.getCmp('modify-thema-btn').show();
                                }
                            }

                            Ext.toast({ html: esapp.Utils.getTranslation('systemsettingsrefreshed'), title: esapp.Utils.getTranslation('systemsettingsrefreshed'), width: 200, align: 't' });
                        }
                    }
                });
            }
        }];

        //var ip_pc1 = {
        //    items:[{
        //        id: 'ip_pc1',
        //        name: 'ip_pc1',
        //        bind: '{system_setting.ip_pc1}',
        //        xtype: 'displayfield',
        //        fieldLabel: me.form_fieldlabel_ip_pc1,
        //        vtype: 'IPAddress',
        //        msgTarget: 'side',
        //        fieldStyle:'font-weight: bold;',
        //        allowBlank: false,
        //        flex: 2.2
        //    }]
        //};
        //
        //var ip_pc2 = {
        //    items:[{
        //        id: 'ip_pc2',
        //        name: 'ip_pc2',
        //        bind: '{system_setting.ip_pc2}',
        //        xtype: 'displayfield',
        //        fieldLabel: me.form_fieldlabel_ip_pc2,
        //        vtype: 'IPAddress',
        //        msgTarget: 'side',
        //        fieldStyle:'font-weight: bold;',
        //        allowBlank: false,
        //        flex: 2.2
        //    }]
        //};
        //var ip_pc3 = {
        //    items:[{
        //        id: 'ip_pc3',
        //        name: 'ip_pc3',
        //        bind: '{system_setting.ip_pc3}',
        //        xtype: 'displayfield',
        //        fieldLabel: me.form_fieldlabel_ip_pc3,
        //        vtype: 'IPAddress',
        //        msgTarget: 'side',
        //        fieldStyle:'font-weight: bold;',
        //        allowBlank: false,
        //        flex: 2.2
        //    }]
        //};

        //var modify_ips_btn = {
        //    xtype: 'button',
        //    text: esapp.Utils.getTranslation('modify'), // 'Modify',
        //    align:'right',
        //    flex: 0.8,
        //    iconCls: 'fa fa-pencil-square-o',
        //    style: { color: 'white' },
        //    // glyph: 'xf055@FontAwesome',
        //    //scale: 'medium',
        //    scope:me,
        //    handler: function(){
        //        var IPAdminWin = new esapp.view.system.IPAddressAdmin({
        //            params: {}
        //        });
        //        IPAdminWin.show();
        //    }
        //};

        var systemsettingsstore  = Ext.data.StoreManager.lookup('SystemSettingsStore');
        var systemsettingsrecord = systemsettingsstore.getModel().load(0, {
            scope: me,
            failure: function(record, operation) {
                //console.info('failure');
            },
            success: function(record, operation) {
                me.type_install = record.data.type_installation;
                me.pcrole = record.data.role;
                me.thema = record.data.thema;

                if (me.pcrole == ''){
                    //console.info(Ext.getCmp('modify-role-btn'));
                    Ext.getCmp('modify-role-btn').show();
                    Ext.getCmp('modify-role-btn').fireHandler();
                }

                // IN WINDOWS VERSION THEMA MUST BE CHANGEABLE!
                if (esapp.globals['typeinstallation'] != 'windows'){
                    if (me.thema != ''){
                        Ext.getCmp('modify-thema-btn').hide();
                    }
                }

                //var ipadresses_fieldset = Ext.getCmp('ipaddresses');
                //if (me.type_install == 'Full'){
                //    ipadresses_fieldset.add(ip_pc1);
                //    ipadresses_fieldset.add(ip_pc2);
                //    ip_pc3.items.push(modify_ips_btn);
                //    ipadresses_fieldset.add(ip_pc3);
                //}
                //else {
                //    ipadresses_fieldset.add(ip_pc1);
                //    ip_pc2.items.push(modify_ips_btn);
                //    ipadresses_fieldset.add(ip_pc2);
                //}
            }
        });

        me.dockedItems=  [{
            dock: 'bottom',
            xtype: 'toolbar',
            items : [{
                text: esapp.Utils.getTranslation('createsystemreport'), // 'Create System Report',
                scope: me,
                hidden:  hiddenForWindowsVersion,
                iconCls: 'fa fa-download fa-2x',
                style: { color: 'blue' },
                scale: 'medium',
                disabled: false,
                handler: function () {
                    // if (!Ext.fly('app-upload-frame')) {
                    //     var body = Ext.getBody();
                    //     var downloadFrame = body.createChild({
                    //         tag: 'iframe',
                    //         cls: 'x-hidden',
                    //         id: 'app-upload-frame',
                    //         name: 'uploadframe'
                    //     });
                    //
                    //     var downloadForm = body.createChild({
                    //         tag: 'form',
                    //         cls: 'x-hidden',
                    //         id: 'app-upload-form',
                    //         target: 'app-upload-frame'
                    //     });
                    // }


                    if (!Ext.fly('frmExportDummy')) {
                        var frm = document.createElement('form');
                        frm.id = 'frmExportDummy';
                        frm.name = frm.id;
                        frm.className = 'x-hidden';
                        document.body.appendChild(frm);
                    }

                    Ext.Ajax.request({
                        method: 'POST',
                        url: 'systemsettings/systemreport',
                        isUpload: true,
                        form: Ext.fly('frmExportDummy'),
                        success: function(response, opts){
                            var result = Ext.JSON.decode(response.responseText);
                            if (!result.success){
                                console.info(response.status);
                               // Ext.toast({ html: 'Download system report', title: 'System report', width: 200, align: 't' });
                            }
                        },
                        failure: function(response, opts) {
                            console.info(response.status);
                        }
                    });
                }
            },{
                text: esapp.Utils.getTranslation('createinstallreport'), // 'Create Install Report',
                scope:me,
                hidden:  hiddenForWindowsVersion,
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
                text: esapp.Utils.getTranslation('resettofactorysettings'), // 'Reset to factory settings',
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
                                Ext.toast({ html: esapp.Utils.getTranslation('resettofactorysettingstext'), title: esapp.Utils.getTranslation('resettofactorysettings'), width: 200, align: 't' });
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
                                    Ext.getCmp('datamanagementmain').setDirtyStore(true);
                                    Ext.getCmp('acquisitionmain').setDirtyStore(true);
                                }
                            });
                        },
                        failure: function(response, opts) {
                            console.info(response.status);
                        }
                    });
                }
            },{
                text: esapp.Utils.getTranslation('save'), // 'Save',
                scope:me,
                iconCls: 'fa fa-save fa-2x',    // 'icon-disk',
                style: { color: 'lightblue' },
                scale: 'medium',
                disabled: false,
                handler: function(){
                    // me.onHandleAction('Save','save');
                    var SystemSettingChanges = me.getSession().getChanges();
                    if (SystemSettingChanges != null){
                        // console.info(me.getSession().getChanges());
                        me.getSession().getSaveBatch().start();
                        Ext.toast({ html: esapp.Utils.getTranslation('systemsettingssaved'), title: esapp.Utils.getTranslation('systemsettingssaved'), width: 200, align: 't' });

                        // console.info(SystemSettingChanges.SystemSetting.U[0].hasOwnProperty('data_dir'));
                        if (SystemSettingChanges.SystemSetting.U[0].hasOwnProperty('data_dir')){
                            Ext.getCmp('datamanagementmain').setDirtyStore(true);
                            Ext.getCmp('acquisitionmain').setDirtyStore(true);
                        }

                        // var datasetsstore  = Ext.data.StoreManager.lookup('DataSetsStore');
                        // if (datasetsstore.isStore) {
                        //     // datasetsstore.proxy.extraParams = {force: true};
                        //     // datasetsstore.load();
                        // }
                    }
                }
            }]
        }];

        me.items = [{
            margin:'0 15 5 0',
            items: [{
                xtype: 'fieldset',
                title: me.fieldset_title_system_settings,
                collapsible:false,
                height:'800',
                defaults: {
                    width: 350,
                    labelWidth: 100
                },
                items: [{
                    xtype: 'fieldset',
                    hidden:  hiddenForWindowsVersion,
                    title: '',
                    collapsible:false,
                    padding: 5,
                    defaults: {
                        labelWidth: 100,
                        layout: 'hbox'
                    },
                    items:[{
                        xtype: 'container',
                        items: [{
                            id: 'type_of_install',
                            name: 'type_of_install',
                            bind: '{system_setting.type_installation}',
                            xtype: 'displayfield',
                            fieldLabel: me.form_fieldlabel_type_of_install,
                            fieldStyle: 'font-weight: bold;'
                        }]
                    },{
                        xtype: 'container',
                        items: [{
                            id: 'role',
                            name: 'role',
                            bind: '{system_setting.role}',
                            xtype: 'displayfield',
                            fieldLabel: me.form_fieldlabel_role,
                            fieldStyle: 'font-weight: bold;',
                            flex: 2.2
                        },{
                            xtype: 'button',
                            id: 'modify-role-btn',
                            hidden: true,
                            text: esapp.Utils.getTranslation('modify'),    // 'Modify',
                            flex: 0.8,
                            iconCls: 'fa fa-pencil-square-o',
                            style: { color: 'white' },
                            // glyph: 'xf055@FontAwesome',
                            //scale: 'medium',
                            scope:me,
                            handler: function(){
                                var PCRoleAdminWin = new esapp.view.system.PCRoleAdmin({
                                    params: {
                                        currentrole: Ext.getCmp('role').getValue()
                                    }
                                });
                                PCRoleAdminWin.show();
                            }
                        }]
                    }]
                },{
                    xtype: 'fieldset',
                    title: '',
                    collapsible:false,
                    padding: 10,
                    defaults: {
                        labelWidth: 100,
                        layout: 'hbox'
                    },
                    items:[{
                       items:[{
                           id: 'current_mode',
                           hidden:  hiddenForWindowsVersion,
                           name: 'current_mode',
                           bind: '{system_setting.current_mode}',
                           xtype: 'displayfield',
                           fieldLabel: me.form_fieldlabel_current_mode,
                           fieldStyle:'font-weight: bold;',
                           flex: 2.2
                        //},{
                        //    xtype: 'button',
                        //    text: esapp.Utils.getTranslation('modify'),    // 'Modify',
                        //    flex: 0.8,
                        //    iconCls: 'fa fa-pencil-square-o',
                        //    style: { color: 'white' },
                        //    // glyph: 'xf055@FontAwesome',
                        //    //scale: 'medium',
                        //    scope:me,
                        //    handler: function(){
                        //        var PCModeAdminWin = new esapp.view.system.PCModeAdmin({
                        //            params: {
                        //                currentmode: Ext.getCmp('current_mode').getValue().toLowerCase()
                        //            }
                        //        });
                        //        PCModeAdminWin.show();
                        //    }
                        }]
                    },{
                       items:[{
                           id: 'active_version',
                           name: 'active_version',
                           hidden:  hiddenForWindowsVersion,
                           bind: '{system_setting.active_version}',
                           xtype: 'displayfield',
                           fieldLabel: me.form_fieldlabel_active_verion,
                           fieldStyle:'font-weight: bold;',
                           flex: 2.2
                        },{
                            xtype: 'button',
                            hidden:  hiddenForWindowsVersion,
                            text: esapp.Utils.getTranslation('modify'),    // 'Modify',
                            flex: 0.8,
                            iconCls: 'fa fa-pencil-square-o',
                            style: { color: 'white' },
                            //scale: 'medium',
                            scope:me,
                            handler: function(){
                                Ext.Msg.alert('Active version change disabled',
                                    'The active version change has been disabled<BR>' +
                                    'In the Administration Manual it is explained how to change the version manually.');

                                // var PCVersionAdminWin = new esapp.view.system.PCVersionAdmin({
                                //     params: {
                                //         currentversion: Ext.getCmp('active_version').getValue()
                                //     }
                                // });
                                // PCVersionAdminWin.show();
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
                            id: 'modify-thema-btn',
                            text: esapp.Utils.getTranslation('modify'),    // 'Modify',
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
                            text: esapp.Utils.getTranslation('modify'),    // 'Modify',
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
                //},{
                //    xtype: 'fieldset',
                //    title: me.fieldset_title_ipaddresses,  // '<b>IP addresses</b>',
                //    id: 'ipaddresses',
                //    name: 'ipaddresses',
                //    collapsible:false,
                //    padding: 10,
                //    defaults: {
                //        labelWidth: 100,
                //        layout: 'hbox'
                //    }
                }]
            },{
                xtype: 'fieldset',
                title: me.fieldset_title_proxy_settings,
                collapsible:false,
                defaults: {
                    width: 350,
                    labelWidth: 120
                },
                items:[{
                   id: 'proxyhost',
                   name: 'proxyhost',
                   bind: '{system_setting.proxy_host}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_proxy_host,
                   style:'font-weight: bold;',
                   allowBlank: true,
                   disabled: false
                },{
                   id: 'proxyport',
                   name: 'proxyport',
                   bind: '{system_setting.proxy_port}',
                   xtype: 'numberfield',
                   fieldLabel: me.form_fieldlabel_proxy_port,
                   style:'font-weight: bold;',
                   width: 250,
                   allowBlank: true,
                   disabled: false
                },{
                   id: 'proxyuser',
                   name: 'proxyuser',
                   bind: '{system_setting.proxy_user}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_proxy_user,
                   style:'font-weight: bold;',
                   allowBlank: true,
                   disabled: false
                },{
                   id: 'proxyuserpwd',
                   name: 'proxyuserpwd',
                   bind: '{system_setting.proxy_userpwd}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_proxy_userpwd,
                   style:'font-weight: bold;',
                   allowBlank: true,
                   disabled: false
                }]
            }]
        },{
            items: [{
                xtype: 'fieldset',
                title: me.fieldset_title_path_settings,
                collapsible:false,
                defaults: {
                    width: 450,
                    labelWidth: 120,
                    layout: 'hbox'
                },
                items:[{
                   id: 'base_dir',
                   name: 'base_dir',
                   bind: '{system_setting.base_dir}',
                   xtype: 'displayfield',
                   fieldLabel: me.form_fieldlabel_base_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                },{
                   id: 'base_tmp_dir',
                   name: 'base_tmp_dir',
                   bind: '{system_setting.base_tmp_dir}',
                   xtype: 'displayfield',
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
                   hidden:  hiddenForWindowsVersion,
                   bind: '{system_setting.ingest_dir}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_ingest_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                },{
                   id: 'static_data_dir',
                   name: 'static_data_dir',
                   hidden:  hiddenForWindowsVersion,
                   bind: '{system_setting.static_data_dir}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_static_data_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                },{
                   width: 450+145,
                   defaults: {
                       margin: '0 5 5 0'
                   },
                   items:[{
                        id: 'archive_dir',
                        name: 'archive_dir',
                        disabled:  hiddenForWindowsVersion,
                        bind: '{system_setting.archive_dir}',
                        xtype: 'textfield',
                        vtype: 'directory',
                        fieldLabel: me.form_fieldlabel_archive_dir,
                        style:'font-weight: bold;',
                        allowBlank: false,
                        width: 450
                        //,listeners: {
                        //    change: function (cmp, value) {
                        //        console.info(cmp);
                        //        console.info(value);
                        //
                        //    }
                        //}
                    //},{
                    //    id: 'choose_archive_dir',
                    //    xtype: 'fileuploadfield',       // <input type="file" webkitdirectory directory multiple mozdirectory msdirectory odirectory/>
                    //    buttonText: esapp.Utils.getTranslation('...'),
                    //    width: 30,
                    //    buttonOnly: true,
                    //    hideLabel: true,
                    //    vtype: 'directory',
                    //    listeners: {
                    //        change: function (fld, value, x, y) {
                    //            //console.log(fld.files[0].mozFullPath);
                    //
                    //            console.info(fld);
                    //            console.info(value);
                    //            console.info(x);
                    //            console.info(y);
                    //            Ext.getCmp('archive_dir').setValue(value);
                    //        }
                    //        //,afterrender:function(cmp){
                    //        //    cmp.fileInputEl.set({
                    //        //        'webkitdirectory': '',
                    //        //        'directory': '',
                    //        //        'mozdirectory': '',
                    //        //        'msdirectory': '',
                    //        //        'odirectory': ''
                    //        //    });
                    //        //}
                    //    },
                    //    //iconCls: 'fa fa-pencil-square-o',
                    //    //style: { color: 'white' },
                    //    //scale: 'medium',
                    //    scope:me,
                    //    handler: function(){
                    //
                    //    }
                    },{
                        xtype: 'splitbutton',
                        text: esapp.Utils.getTranslation('ingest_archive'),
                        disabled:  hiddenForWindowsVersion,
                        width: 140,
                        iconCls: '',    // 'fa fa-spinner',
                        style: { color: 'white'},
                        //scale: 'medium',
                        //scope:me,
                        formBind: false,
                        name: 'ingestarchivebtn',
                        service: 'ingestarchive',
                        task: 'status',
                        menu: {
                            disabled:  hiddenForWindowsVersion,
                            width: 150,
                            margin: '0 0 10 0',
                            floating: true,  // usually you want this set to True (default)
                            collapseDirection: 'right',
                            defaults: {
                                disabled:  hiddenForWindowsVersion,
                                align: 'right'
                            },
                            items: [
                                // these will render as dropdown menu items when the arrow is clicked:
                                {   text: esapp.Utils.getTranslation('run'),    // 'Run',
                                    name: 'run_ingestarchive',
                                    service: 'ingestarchive',
                                    task: 'run',
                                    // iconCls: 'fa-play-circle-o', // xf01d   // fa-play xf04b
                                    glyph: 'xf04b@FontAwesome',
                                    cls:'menu-glyph-color-green',
                                    // style: { color: 'green' },
                                    handler: 'execServiceTask'
                                },
                                {   text: esapp.Utils.getTranslation('stop'),    // 'Stop',
                                    name: 'stop_ingestarchive',
                                    service: 'ingestarchive',
                                    task: 'stop',
                                    // iconCls: 'fa fa-stop',
                                    glyph: 'xf04d@FontAwesome',
                                    cls:'menu-glyph-color-red',
                                    // style: { color: 'red' },
                                    handler: 'execServiceTask'
                                },
                                {   text: esapp.Utils.getTranslation('restart')+'          ',    // 'Restart          ',
                                    name: 'restart_ingestarchive',
                                    service: 'ingestarchive',
                                    task: 'restart',
                                    // iconCls: 'fa fa-refresh',
                                    glyph: 'xf021@FontAwesome',
                                    cls:'menu-glyph-color-orange',
                                    // style: { color: 'orange' },
                                    handler: 'execServiceTask'
                                },
                                {
                                    text: esapp.Utils.getTranslation('viewlogfile'),    // 'View log file',
                                    name: 'view_logfile_ingestarchive',
                                    service: 'ingestarchive',
                                    task: 'logfile',
                                    iconCls:'log-icon-small',
                                    handler: 'viewLogFile'
                                }
                            ]
                        },
                        listeners: {
                            beforerender: 'execServiceTask'
                        }
                        ,handler: 'execServiceTask'
                    }]
                },{
                   id: 'eumetcast_files_dir',
                   name: 'eumetcast_files_dir',
                   hidden:  hiddenForWindowsVersion,
                   bind: '{system_setting.eumetcast_files_dir}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_eumetcast_files_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                },{
                   id: 'get_eumetcast_output_dir',
                   name: 'get_eumetcast_output_dir',
                   hidden:  hiddenForWindowsVersion,
                   bind: '{system_setting.get_eumetcast_output_dir}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_get_eumetcast_output_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                },{
                   id: 'get_internet_output_dir',
                   name: 'get_internet_output_dir',
                   hidden:  hiddenForWindowsVersion,
                   bind: '{system_setting.get_internet_output_dir}',
                   xtype: 'textfield',
                   fieldLabel: me.form_fieldlabel_get_internet_output_dir,
                   style:'font-weight: bold;',
                   allowBlank: false
                }]
            },{
                xtype: 'fieldset',
                title: me.fieldset_title_database_connection_settings,
                collapsible:false,
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
