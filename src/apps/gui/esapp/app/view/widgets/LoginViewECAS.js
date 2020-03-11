
Ext.define("esapp.view.widgets.LoginViewECAS",{
    extend: "Ext.container.Container",
 
    requires: [
        "esapp.view.widgets.LoginViewECASController",
        "esapp.view.widgets.LoginViewECASModel",

        'Ext.layout.container.Fit',
        'Ext.app.ViewModel'
        ,'Ext.util.Cookies'
    ],

    controller: "widgets-loginview-ecas",
    viewModel: {
        type: "widgets-loginview-ecas"
    },
    //,viewModel:'default'

    alias:'widget.loginviewECAS'
    ,layout:'fit'
    ,padding:0
    ,margin:0
    ,style: {
        'background-color': '#157FCC'
    }

    // fire all listeners in the scope of this window
    ,defaultListenerScope:true

    // hold references here
    ,referenceHolder:true

    ,initComponent: function () {
        var me = this
            ,SetupLogin = esapp.LoginSetup
        ;

        // install listeners on Setup
        SetupLogin.on({
             scope:me
            ,setupready:me.setupLogout
            ,setupfail:me.failLogin
        });

        me.listeners = {
            beforerender: function(){
                var strCall = 'undefined';

                // separating the GET parameters from the current URL
                var getParams = document.URL.split("?");
                // transforming the GET parameters into a dictionnary
                var params = Ext.urlDecode(getParams[getParams.length - 1]);

                if (esapp.Utils.objectExists(params.ticket) && params.ticket != '' && esapp.Utils.objectExists(params.strCall && params.strCall != '')){

                    strCall = encodeURIComponent(params.strCall+"?strCall=")+encodeURIComponent(params.strCall);  // Encode the strCall value and add strCall to it, encoded

                    Ext.Ajax.request({
                        method: 'POST',
                        params: {
                            ticket: params.ticket,
                            strCall: strCall
                        },
                        url: 'checkECASlogin',
                        callback: function (callinfo, responseOK, response) {
                            var userinfo = Ext.JSON.decode(response.responseText.trim()).user;
                            // console.info(userinfo);
                            esapp.setUser(userinfo);
                            me.setupLogout();
                            window.history.pushState(userinfo, "eStation2 - Earth Observation Processing Service", window.location.href.split("?")[0]);
                        },
                        success: function (result, request) {
                        },
                        failure: function (result, request) {
                        }
                    });
                }
                else if (Ext.util.Cookies.get('estation2_userid') != null){
                    var userinfo = {
                        userid: Ext.util.Cookies.get('estation2_userid'),
                        username: Ext.util.Cookies.get('estation2_username'),
                        email: Ext.util.Cookies.get('estation2_useremail'),
                        userlevel: Ext.util.Cookies.get('estation2_userlevel'),
                        prefered_language: Ext.util.Cookies.get('estation2_userlanguage')
                    };

                    esapp.setUser(userinfo);
                    me.setupLogout();
                }
            }
        };

        me.loginItems = [{
            xtype: 'form'
            , padding: 0

            // for easy access to the form from listeners
            , reference: 'loginForm'
            , bodyStyle: {
                'background-color': '#157FCC'
            }
            , defaults: {
                anchor: '100%'
                , allowBlank: false
                , enableKeyEvents: true
                , xtype: 'textfield'
                , listeners: {
                    keypress: 'onKeyPress'
                }
            }
            , layout: 'hbox'
            , items: [{
            //     bind: '{username}'
            //     // needed for defaultButton
            //     , itemId: 'username'
            //     , hideLabel: true
            //     , fieldLabel: esapp.Utils.getTranslation('username')    // 'User Name'
            //     , emptyText: esapp.Utils.getTranslation('username')
            //     , margin: '4 5 0 5'
            //     , width: 100
            // }, {
            //     bind: '{password}'
            //     , hideLabel: true
            //     , fieldLabel: esapp.Utils.getTranslation('password')    // 'Password'
            //     , emptyText: esapp.Utils.getTranslation('password')
            //     , inputType: 'password'
            //     , margin: '4 5 0 5'
            //     , width: 100
            // }, {
                xtype: 'button'
                , text: esapp.Utils.getTranslation('login')  // 'Login'
                , margin: '4 10 0 5'
                , formBind: false
                , handler: 'onLoginClick'
                // , menu: {
                //     items: [{
                //         text: esapp.Utils.getTranslation('forgot_password')   // 'Forgot password?'
                //         //, iconCls: 'fa fa-lock'
                //         , glyph: 'xf023@FontAwesome'
                //         , cls:'menu-glyph-color-red'
                //         // style: { color: 'orange' },
                //         , handler: 'resetPassword'
                //     }]
                // }
            }, {
                xtype: 'box'
                , html: esapp.Utils.getTranslation('or')   // 'or'
                , cls: 'text-white'
                , margin: '8 5 0 0'
            }, {
                xtype: 'button'
                , text: esapp.Utils.getTranslation('register')   // 'Register'
                , margin: '4 45 0 5'
                , formBind: false
                , handler: 'onRegisterClick'
            }]
        }];

        me.logoutItems = [{     // Ext.create('Ext.container.Container', {
            xtype: 'container'
            , padding: 0

            // for easy access to the form from listeners
            , reference: 'logoutForm'
            , bodyStyle: {
                'background-color': '#157FCC'
            }
            , defaults: {
                anchor: '100%'
            }
            , layout: 'hbox'
            , items: [{
                xtype: 'box'
                , reference: 'UserLoggedIn'
                , html: esapp.Utils.getTranslation('hello') + ' '   // 'Hello '
                , cls: 'text-white'
                , margin: '8 5 0 0'
            }, {
                xtype: 'button'
                , text: esapp.Utils.getTranslation('logout')   // 'Logout'
                , margin: '4 45 0 5'
                , formBind: false
                , handler: 'onLogoutClick'
            }]
        }];

        me.items = me.loginItems;

        me.callParent();
    }

    // auto-focus username
    ,defaultButton:'username'

    /**
     * Login button click handler
     * @private
     */
    ,onLoginClick:function() {
        var  me = this
            // ,data = me.getViewModel().linkData
            ,cookieExists = false
        ;

        if (!cookieExists){

        }

        var strPathRedirect=window.location.href;
        // var strEcasCall="https://ecas.cc.cec.eu.int:7002/cas/login?" +
        //                 "service="+encodeURIComponent(strPathRedirect +'?')+"strCall"+encodeURIComponent('='+strPathRedirect)+"&userDetails=FLAG_USER_DETAILS";
        var strEcasCall="https://webgate.ec.europa.eu/cas/login?" +
                        "service="+encodeURIComponent(strPathRedirect +'?')+"strCall"+encodeURIComponent('='+strPathRedirect)+"&userDetails=FLAG_USER_DETAILS";
        window.location.href = strEcasCall;

        // var myWin = Ext.create("Ext.window.Window", {
        //     title: '',
        //     border: false,
        //     frame: false,
        //     modal: true,
        //     closable: true,
        //     maximized: true,
        //     autoEl : {
        //         tag : "embed",
        //         src : strEcasCall
        //     }
        //     // items: iframe
        //     // html: '<iframe src="' + strEcasCall + '" width="100%" height="100%" ></iframe>'
        // })
        //
        // myWin.show();

    } // eo function onLoginClick

    /**
     * Login button click handler
     * @private
     */
    ,onLogoutClick:function() {
        var  me = this;

        esapp.logout();

        me.removeAll();
        me.add(me.loginItems);
        me.toggleUserFunctionality();

    } // eo function onLoginClick

    /**
     * Handles login success and shows logout button
     * @private
     * @param responce
     */
    ,setupLogout:function() {
        var  me = this;
        me.removeAll();
        me.add(me.logoutItems);
        me.lookupReference('UserLoggedIn').setHtml(esapp.Utils.getTranslation('hello') + ' ' + esapp.getUser().username);

        me.toggleUserFunctionality();

    } // eo function setupLogout


    /**
     * Register button click handler
     * @private
     */
    ,onRegisterClick:function() {
        // var ECASRegisterURL = 'https://ecas.cc.cec.eu.int:7002/cas/login?';
        var ECASRegisterURL = 'https://webgate.ec.europa.eu/cas/login?';
        var win = window.open(ECASRegisterURL, '_blank');
        win.focus();
        // new esapp.view.widgets.Register();
    } // eo function onRegisterClick

    /**
     * Handles login fail and shows message
     * @private
     * @param responce
     */
    ,failLogin:function() {
        var  me = this;
        Ext.Msg.show({
             title:'Error'
            ,msg:esapp.Utils.getTranslation('username_password_incorrect')    // Username or password incorrect!
            ,icon:Ext.Msg.ERROR
            ,buttons:Ext.Msg.OK
        });

    } // eo function failLogin

    /**
     * Handles Enter press
     * @private
     * @param {Ext.form.field.Field} field
     * @param {Ext.EventObject} e
     */
    ,onKeyPress:function(field, e) {
        var  me = this
            ,form = me.lookupReference('loginForm')
        ;
        if(form.isValid() && Ext.EventObject.ENTER === e.getKey()) {
            me.onLoginClick();
        }

    } // eo function onKeyPress

    ,toggleUserFunctionality:function() {
        var me = this;
        var user = esapp.getUser();
        var analysisWorkspaces = Ext.ComponentQuery.query('analysisworkspace');
        var mapViewWindows = Ext.ComponentQuery.query('mapview-window');
        var tsChartWindows = Ext.ComponentQuery.query('timeserieschart-window');
        var addWorkspaceBtn = Ext.getCmp('analysismain').lookupReference('analysismain_addworkspacebtn');
        // var mapTemplateBtn = Ext.getCmp('analysismain').lookupReference('analysismain_maptemplatebtn');
        // var tsChartTemplateBtn = Ext.getCmp('analysismain').lookupReference('analysismain_graph_templatebtn');
        // var tsDrawPropertiesStore  = Ext.data.StoreManager.lookup('TSDrawPropertiesStore');

        if (user != null && user != 'undefined'){
            // tsDrawPropertiesStore.proxy.extraParams = {userid: user.userid, graph_tpl_name: 'default'};
            // tsDrawPropertiesStore.load();
            if (addWorkspaceBtn != null){
                addWorkspaceBtn.show();
            }
            var UserWorkspacesStore = Ext.StoreManager.lookup('UserWorkspacesStore');
            UserWorkspacesStore.proxy.extraParams = {userid: esapp.getUser().userid};
            UserWorkspacesStore.load({
                callback: function (records, options, success) {
                    var activateTab = false;
                    records.forEach(function(workspace,id){
                        if (workspace.get('pinned')){
                            // open workspace
                            Ext.getCmp('analysismain').getController().openWorkspace(workspace,activateTab);
                        }
                    });
                }
            });
            // UserWorkspacesStore.each(function(workspace,id){
            //     console.info(workspace);
            // });
            if (analysisWorkspaces != []) {
                Ext.Object.each(analysisWorkspaces, function (id, workspace, thisObj) {
                    workspace.lookupReference('maptemplateadminbtn_' + workspace.id.replace(/-/g, '_')).show();
                    workspace.lookupReference('graphtemplateadminbtn_' + workspace.id.replace(/-/g, '_')).show();
                    // workspace.lookupReference('analysismain_legendsbtn_'+workspace.id.replace(/-/g,'_')).show();
                    workspace.lookupReference('analysismain_layersbtn_' + workspace.id.replace(/-/g, '_')).show();
                    if (esapp.globals['typeinstallation'] != 'jrc_online') {
                        workspace.lookupReference('analysismain_logosbtn_' + workspace.id.replace(/-/g, '_')).show();
                    }

                    if (workspace.workspaceid != 'defaultworkspace') {
                        workspace.lookupReference('saveWorkspaceBtn').show();
                    }
                    else {
                        workspace.lookupReference('saveDefaultWorkspaceAsBtn').show();
                    }

                    if (Ext.isObject(workspace.lookupReference('maptemplateadminbtn_' + workspace.id.replace(/-/g, '_')).mapTemplateAdminPanel)) {
                        workspace.lookupReference('maptemplateadminbtn_' + workspace.id.replace(/-/g, '_')).mapTemplateAdminPanel.setDirtyStore(true);
                    }
                    if (Ext.isObject(workspace.lookupReference('graphtemplateadminbtn_' + workspace.id.replace(/-/g, '_')).graphTemplateAdminPanel)) {
                        workspace.lookupReference('graphtemplateadminbtn_' + workspace.id.replace(/-/g, '_')).graphTemplateAdminPanel.setDirtyStore(true);
                    }
                });
            }
            // mapTemplateBtn.show();
            if (mapViewWindows != []) {
                Ext.Object.each(mapViewWindows, function (id, mapview_window, thisObj) {
                    if (mapview_window.templatename != '') {
                        mapview_window.isTemplate = true;
                        if (Ext.isObject(Ext.fly('mapview_title_templatename_' + mapview_window.id))) {
                            Ext.fly('mapview_title_templatename_' + mapview_window.id).dom.innerHTML = mapview_window.templatename;
                        }
                    }
                    mapview_window.lookupReference('saveMapTemplate_' + mapview_window.id.replace(/-/g, '_')).show();
                });
            }
            // Ext.getCmp('userMapTemplates').setDirtyStore(true);

            // tsChartTemplateBtn.show();
            if (tsChartWindows != []) {
                Ext.Object.each(tsChartWindows, function (id, tschart_window, thisObj) {
                    if (tschart_window.graph_tpl_name != '' && tschart_window.graph_tpl_name != 'default') {
                        tschart_window.isTemplate = true;
                        if (Ext.isObject(Ext.fly('graphview_title_templatename_' + tschart_window.id))) {
                            Ext.fly('graphview_title_templatename_' + tschart_window.id).dom.innerHTML = tschart_window.graph_tpl_name;
                        }
                    }
                    tschart_window.lookupReference('changeSelectedProductsAndTimeframe_' + tschart_window.id.replace(/-/g, '_')).show();
                    tschart_window.lookupReference('saveGraphTemplate_' + tschart_window.id.replace(/-/g, '_')).show();
                });
            }
            // Ext.getCmp('userGraphTemplates').setDirtyStore(true);
        }
        else {
            // tsDrawPropertiesStore.proxy.extraParams = {};
            // tsDrawPropertiesStore.load();
            if (addWorkspaceBtn != null){
                addWorkspaceBtn.hide();
            }

            if (analysisWorkspaces != []) {
                Ext.Object.each(analysisWorkspaces, function (id, workspace, thisObj) {
                    if (workspace.workspaceid != 'defaultworkspace') {
                        workspace.close();
                    }
                    else {
                        // mapTemplateBtn.hide();
                        if (mapViewWindows != []) {
                            Ext.Object.each(mapViewWindows, function (id, mapview_window, thisObj) {
                                if (mapview_window.isTemplate) {
                                    mapview_window.isTemplate = false;
                                    if (Ext.isObject(Ext.fly('mapview_title_templatename_' + mapview_window.id))) {
                                        Ext.fly('mapview_title_templatename_' + mapview_window.id).dom.innerHTML = '';
                                    }
                                }
                                mapview_window.lookupReference('saveMapTemplate_' + mapview_window.id.replace(/-/g, '_')).hide();
                            });
                        }
                        // Ext.getCmp('userMapTemplates').hide();

                        // tsChartTemplateBtn.hide();
                        if (tsChartWindows != []) {
                            Ext.Object.each(tsChartWindows, function (id, tschart_window, thisObj) {
                                if (tschart_window.isTemplate) {
                                    tschart_window.isTemplate = false;
                                    if (Ext.isObject(Ext.fly('graphview_title_templatename_' + tschart_window.id))) {
                                        Ext.fly('graphview_title_templatename_' + tschart_window.id).dom.innerHTML = '';
                                    }
                                }
                                tschart_window.lookupReference('changeSelectedProductsAndTimeframe_' + tschart_window.id.replace(/-/g, '_')).hide();
                                tschart_window.lookupReference('saveGraphTemplate_' + tschart_window.id.replace(/-/g, '_')).hide();
                            });
                        }
                        // Ext.getCmp('userGraphTemplates').hide();

                        workspace.lookupReference('maptemplateadminbtn_' + workspace.id.replace(/-/g, '_')).hide();
                        workspace.lookupReference('graphtemplateadminbtn_' + workspace.id.replace(/-/g, '_')).hide();

                        workspace.lookupReference('analysismain_legendsbtn_' + workspace.id.replace(/-/g, '_')).hide();
                        workspace.lookupReference('analysismain_layersbtn_' + workspace.id.replace(/-/g, '_')).hide();
                        workspace.lookupReference('analysismain_logosbtn_' + workspace.id.replace(/-/g, '_')).hide();

                        workspace.lookupReference('saveDefaultWorkspaceAsBtn').hide();
                        if (Ext.isObject(workspace.lookupReference('maptemplateadminbtn_' + workspace.id.replace(/-/g, '_')).mapTemplateAdminPanel)) {
                            workspace.lookupReference('maptemplateadminbtn_' + workspace.id.replace(/-/g, '_')).mapTemplateAdminPanel.hide();
                        }
                        if (Ext.isObject(workspace.lookupReference('graphtemplateadminbtn_' + workspace.id.replace(/-/g, '_')).graphTemplateAdminPanel)) {
                            workspace.lookupReference('graphtemplateadminbtn_' + workspace.id.replace(/-/g, '_')).graphTemplateAdminPanel.hide();
                        }
                    }
                });
            }
        }
    }

    ,__toggleUserFunctionality:function() {
        var me = this;
        var mapTemplateBtn = Ext.getCmp('analysismain').lookupReference('analysismain_maptemplatebtn');
        var mapViewWindows = Ext.ComponentQuery.query('mapview-window');
        var tsChartTemplateBtn = Ext.getCmp('analysismain').lookupReference('analysismain_graph_templatebtn');
        var tsChartWindows = Ext.ComponentQuery.query('timeserieschart-window');
        var tsDrawPropertiesStore  = Ext.data.StoreManager.lookup('TSDrawPropertiesStore');
        var user = esapp.getUser();

        if (esapp.getUser() != null && esapp.getUser() != 'undefined'){
            tsDrawPropertiesStore.proxy.extraParams = {userid: user.userid, graph_tpl_name: 'default'};
            tsDrawPropertiesStore.load();

            mapTemplateBtn.show();

            Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                if (mapview_window.templatename != ''){
                    mapview_window.isTemplate = true;
                    Ext.fly('mapview_title_templatename_' + mapview_window.id).dom.innerHTML = mapview_window.templatename;
                }
                mapview_window.lookupReference('saveMapTemplate_'+mapview_window.id.replace(/-/g,'_')).show();
            });
            Ext.getCmp('userMapTemplates').setDirtyStore(true);

            tsChartTemplateBtn.show();
            Ext.Object.each(tsChartWindows, function(id, tschart_window, thisObj) {
                if (tschart_window.graph_tpl_name != '' && tschart_window.graph_tpl_name != 'default'){
                    tschart_window.isTemplate = true;
                    Ext.fly('graphview_title_templatename_' + tschart_window.id).dom.innerHTML = tschart_window.graph_tpl_name;
                }
                tschart_window.lookupReference('saveGraphTemplate_'+tschart_window.id.replace(/-/g,'_')).show();
            });
            Ext.getCmp('userGraphTemplates').setDirtyStore(true);
        }
        else {
            tsDrawPropertiesStore.proxy.extraParams = {};
            tsDrawPropertiesStore.load();

            mapTemplateBtn.hide();

            Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                if (mapview_window.isTemplate){
                    mapview_window.isTemplate = false;
                    Ext.fly('mapview_title_templatename_' + mapview_window.id).dom.innerHTML = '';
                }
                mapview_window.lookupReference('saveMapTemplate_'+mapview_window.id.replace(/-/g,'_')).hide();
            });
            Ext.getCmp('userMapTemplates').hide();

            tsChartTemplateBtn.hide();
            Ext.Object.each(tsChartWindows, function(id, tschart_window, thisObj) {
                if (tschart_window.isTemplate){
                    tschart_window.isTemplate = false;
                    Ext.fly('graphview_title_templatename_' + tschart_window.id).dom.innerHTML = '';
                }
                tschart_window.lookupReference('saveGraphTemplate_'+tschart_window.id.replace(/-/g,'_')).hide();
            });
            Ext.getCmp('userGraphTemplates').hide();
        }

    } // eo function failLogin
});