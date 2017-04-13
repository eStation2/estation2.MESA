
Ext.define("esapp.view.widgets.LoginView",{
    extend: "Ext.container.Container",
 
    requires: [
        "esapp.view.widgets.LoginViewController",
        "esapp.view.widgets.LoginViewModel",

        'Ext.layout.container.Fit',
        'Ext.app.ViewModel'
    ],

    controller: "widgets-loginview",
    viewModel: {
        type: "widgets-loginview"
    },
    //,viewModel:'default'

    alias:'widget.loginview'
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
                bind: '{username}'
                // needed for defaultButton
                , itemId: 'username'
                , hideLabel: true
                , fieldLabel: esapp.Utils.getTranslation('username')    // 'User Name'
                , emptyText: esapp.Utils.getTranslation('username')
                , margin: '4 5 0 5'
                , width: 100
            }, {
                bind: '{password}'
                , hideLabel: true
                , fieldLabel: esapp.Utils.getTranslation('password')    // 'Password'
                , emptyText: esapp.Utils.getTranslation('password')
                , inputType: 'password'
                , margin: '4 5 0 5'
                , width: 100
            }, {
                xtype: 'splitbutton'
                , text: esapp.Utils.getTranslation('login')  // 'Login'
                , margin: '4 10 0 5'
                , formBind: false
                , handler: 'onLoginClick'
                , menu: {
                    items: [{
                        text: esapp.Utils.getTranslation('forgot_password')   // 'Forgot password?'
                        //, iconCls: 'fa fa-lock'
                        , glyph: 'xf023@FontAwesome'
                        , cls:'menu-glyph-color-red'
                        // style: { color: 'orange' },
                        , handler: 'resetPassword'
                    }]
                }
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
            ,data = me.getViewModel().linkData
        ;
        //data.password = SparkMD5.hash(data.password);
        esapp.login(data);

    } // eo function onLoginClick

    /**
     * Login button click handler
     * @private
     */
    ,onLogoutClick:function() {
        var  me = this
            ,data = me.getViewModel().linkData
        ;

        esapp.logout();

        me.removeAll();
        me.add(me.loginItems);
        //esapp.setUser(null);
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
        new esapp.view.widgets.Register();
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