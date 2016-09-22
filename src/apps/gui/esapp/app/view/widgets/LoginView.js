
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
                , fieldLabel: 'User Name'
                , emptyText: esapp.Utils.getTranslation('User name')
                , margin: '4 5 0 5'
                , width: 100
            }, {
                bind: '{password}'
                , hideLabel: true
                , fieldLabel: 'Password'
                , emptyText: esapp.Utils.getTranslation('Password')
                , inputType: 'password'
                , margin: '4 5 0 5'
                , width: 100
            }, {
                xtype: 'button'
                , text: 'Login'
                , margin: '4 10 0 5'
                , formBind: true
                , handler: 'onLoginClick'
            }, {
                xtype: 'box'
                , html: 'or'
                , cls: 'text-white'
                , margin: '8 5 0 0'
            }, {
                xtype: 'button'
                , text: 'Register'
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
                , html: 'Hello '
                , cls: 'text-white'
                , margin: '8 5 0 0'
            }, {
                xtype: 'button'
                , text: 'Logout'
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
        //data.password = hex_md5(data.password);
        esapp.login(data);

        //me.close();

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
        //console.info(esapp.getUser());
        //me.close();

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
        me.lookupReference('UserLoggedIn').setHtml('Hello ' + esapp.getUser().username);

    } // eo function setupLogout


    /**
     * Handles login fail and shows message
     * @private
     * @param responce
     */
    ,failLogin:function() {
        var  me = this;
        Ext.Msg.show({
             title:'Error'
            ,msg:'Username or password incorrect!'
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
});