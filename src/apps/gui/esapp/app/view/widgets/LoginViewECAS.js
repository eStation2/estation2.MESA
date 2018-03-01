
Ext.define("esapp.view.widgets.LoginViewECAS",{
    extend: "Ext.container.Container",
 
    requires: [
        "esapp.view.widgets.LoginViewECASController",
        "esapp.view.widgets.LoginViewECASModel",

        'Ext.layout.container.Fit',
        'Ext.app.ViewModel'
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
                        email: Ext.util.Cookies.get('estation2_useremail')
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
        var strEcasCall="https://ecas.cc.cec.eu.int:7002/cas/login?" +
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
        var ECASRegisterURL = 'https://ecas.cc.cec.eu.int:7002/cas/login?';
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
        var  me = this;
        var mapTemplateBtn = Ext.getCmp('analysismain').lookupReference('analysismain_maptemplatebtn');
        var mapViewWindows = Ext.ComponentQuery.query('mapview-window');

        if (esapp.getUser() != null && esapp.getUser() != 'undefined'){
            mapTemplateBtn.show();

            Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                mapview_window.lookupReference('saveMapTemplate_'+mapview_window.id.replace(/-/g,'_')).show();
            });
        }
        else {
            mapTemplateBtn.hide();

            Ext.Object.each(mapViewWindows, function(id, mapview_window, thisObj) {
                mapview_window.lookupReference('saveMapTemplate_'+mapview_window.id.replace(/-/g,'_')).hide();
            });
        }

    } // eo function failLogin
});