Ext.define('esapp.view.analysis.userWorkspaceAdminController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.analysis-userworkspaceadmin'

    ,openWorkspaces: function(){
        var me = this.getView();
        var selectedWorkspaces = me.getSelectionModel().getSelection();
        var analysismainWorkspaceTabPanel = me.owner.up().up().up();
        var analysisWorkspaces = Ext.ComponentQuery.query('analysisworkspace');
        var alreadyOpen = false;
        var workspaceTabToActivate = null;

        for (var i = 0; i < selectedWorkspaces.length; i++) {
           // console.info(selectedWorkspaces[i]);
            Ext.Object.each(analysisWorkspaces, function(id, workspace, thisObj) {
                if (workspace.workspaceid == selectedWorkspaces[i].data.workspaceid){
                    alreadyOpen = true;
                    workspaceTabToActivate = workspace;
                }
            });

            if (selectedWorkspaces[i].get('showindefault')){
                analysismainWorkspaceTabPanel.getController().openWorkspace(selectedWorkspaces[i], true);
            }
            else if (!alreadyOpen){
                analysismainWorkspaceTabPanel.getController().openWorkspace(selectedWorkspaces[i], true);
            }
            else {
                // activate workspace tab
                analysismainWorkspaceTabPanel.setActiveTab(workspaceTabToActivate);
            }
        }
        me.hide();
    }

    ,exportWorkspaces: function(){
        var me = this.getView();
        var selectedWorkspaces = me.getSelectionModel().getSelection();
        var workspaces_json = []

        if (selectedWorkspaces.length < 1){
            Ext.Msg.show({
               title: esapp.Utils.getTranslation('info'),    // 'Info',
               msg: esapp.Utils.getTranslation('please_select_workspace'),    // 'Please select one or more workspaces to export.',
               width: 300,
               buttons: Ext.Msg.OK,
               animEl: '',
               icon: Ext.Msg.WARNING
            });
        }
        else {
            for (var i = 0; i < selectedWorkspaces.length; i++) {
                var wsdata = selectedWorkspaces[i].getData();
                // console.info(wsdata);
                var workspace = {
                    'userid': wsdata['userid'],
                    'workspaceid': wsdata['workspaceid'],
                    'workspacename': wsdata['workspacename'],
                    'isNewWorkspace': false,
                    'pinned': wsdata['pinned'],
                    'showindefault': false,
                    'shownewgraph': wsdata['shownewgraph'],
                    'showbackgroundlayer': wsdata['showbackgroundlayer'],
                    'isrefworkspace': false,
                    'maps':  [],
                    'graphs':  []
                }

                workspaces_json.push(workspace);
            }
            workspaces_json = {
                workspaces:  Ext.encode(workspaces_json)
            };

            // esapp.Utils.download({
            //     method: 'PUT',
            //     url: '/analysis/exportworkspaces',
            //     params: workspaces_json
            // });

            // esapp.Utils.download(workspaces_json);
            // Ext.JSON.encode(workspaces_json)

            if (!Ext.fly('frmExportDummy')) {
                var frm = document.createElement('form');
                frm.id = 'frmExportDummy';
                frm.name = frm.id;
                frm.className = 'x-hidden';
                document.body.appendChild(frm);
            }

            Ext.Ajax.request({
                method: 'POST',
                url: 'analysis/exportworkspaces',
                isUpload: true,
                params: workspaces_json,
                form: Ext.fly('frmExportDummy'),
                success: function(response, opts){
                    var result = Ext.JSON.decode(response.responseText);
                    if (!result.success){
                        // console.info(response.status);
                       // Ext.toast({ html: 'Download system report', title: 'System report', width: 200, align: 't' });
                    }
                },
                failure: function(response, opts) {
                    console.info(response.status);
                }
            });
        }
    }

    ,importWorkspaces:function() {
        var user = esapp.getUser();

        if (user != null && user != 'undefined'){
            var fileUploadWin = new Ext.Window({
                 id:'wsfileupload-win'
                ,layout:'fit'
                ,autoWidth: true
                ,plain: true
                ,modal:true
                ,stateful :false
                ,closable:true
                ,loadMask:true
                ,title:esapp.Utils.getTranslation('import_workspaces') // 'Import workspaces'
                ,items:[{
                    xtype: 'form',
                    fileUpload: true,
                    width: 400,
                    frame: false,
                    title: '',
                    autoHeight: true,
                    bodyStyle: 'padding: 10px 10px 10px 10px;',
                    defaults: {
                        anchor: '90%',
                        allowBlank: false,
                        msgTarget: 'side'
                    },
                    columnCount:1,
                    labelAlign :'top',
                    items: [{
                         xtype: 'hidden'
                        ,name:'importfilename'
                        ,id:'importfilename'
                        ,value: ''
                    },{
                         xtype: 'hidden'
                        ,name:'userid'
                        ,id:'userid'
                        ,value: user.userid
                    },{
                        xtype: 'filefield'
                        ,id: 'workspacesfile'
                        ,name: 'workspacesfile'
                        ,emptyText: esapp.Utils.getTranslation('select_exported_ws_jsonfile') // 'Select exported workspaces file'
                        ,width: 200
                        ,vtype:'JSON'
                        //,labelWidth: 150
                        ,msgTarget: 'side'
                        ,allowBlank: false
                        ,anchor: '100%'
                        ,buttonText: ''
                        ,buttonConfig: {
                            iconCls: 'fa fa-folder-open-o'
                        }
                    }],
                    buttons: [{
                        text: esapp.Utils.getTranslation('btn_import'), // 'Import',
                        handler: function(){
                            if(this.up().up().getForm().isValid()){
                                Ext.getCmp('importfilename').setValue(Ext.getCmp('workspacesfile').lastValue);
                                this.up().up().getForm().submit({
                                    url:'/analysis/importworkspaces',
                                    //scope:this,
                                    waitMsg: esapp.Utils.getTranslation('msg_wait_importing_workspaces'), // 'Importing workspaces...',
                                    success: function(fp, o, x){
                                        var tpl = new Ext.XTemplate(
                                            esapp.Utils.getTranslation('workspaces_saved_under_your_account')+'<br />'
                                            // esapp.Utils.getTranslation('name') + ': {filename}<br />'
                                        );
                                        Ext.Msg.alert('Success', tpl.apply(o.result));

                                        fileUploadWin.close();
                                    }
                                });
                            }
                            else {
                                Ext.Msg.alert(esapp.Utils.getTranslation('warning'), esapp.Utils.getTranslation('vtype_json'));
                            }
                        }
                    },{
                        text: esapp.Utils.getTranslation('btn_txt_reset'), // 'Reset',
                        handler: function(){
                            this.up().up().getForm().reset();
                        }
                    },{
                        text: esapp.Utils.getTranslation('close'), // 'Close',
                        handler: function(){
                            fileUploadWin.close();
                        }
                    }
                    ]
                }]
            });

            fileUploadWin.show();
        }
    }

    ,newWorkspace: function(){
        var me = this.getView();
        var analysismainWorkspaceTabPanel = me.owner.up().up().up();
        analysismainWorkspaceTabPanel.getController().addNewWorkspace();
        me.hide();
    }

    ,deleteWorkspace: function(grid, rowIndex, row){
        var me = this.getView();
        var record = grid.getStore().getAt(rowIndex);

        grid.getStore().remove(record);
        Ext.data.StoreManager.lookup(grid.getStore().config.source).sync();
        me.show(true);
    }
});
