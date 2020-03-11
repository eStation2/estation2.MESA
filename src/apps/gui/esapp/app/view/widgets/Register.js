
Ext.define("esapp.view.widgets.Register",{
    //extend: "Ext.panel.Panel",
    extend: 'Ext.window.Window',
    xtype: 'register',

    requires: [
        "esapp.view.widgets.RegisterController",
        "esapp.view.widgets.RegisterModel",

        'Ext.layout.container.VBox',
        'Ext.form.field.Checkbox',
        'Ext.form.field.Text',
        'Ext.layout.container.HBox'
    ],
    
    controller: "widgets-register",
    viewModel: {
        type: "widgets-register"
    },

    modal: true,
    autoShow: true,
    closable: true,
    draggable: false,
    resizable: false,

    header: {
        titleAlign: 'center',
        height: 40
    },

    layout: {
        type: 'fit',
        align: 'center',
        pack: 'center'
    },
    height: 350,
    width: 425,

    initComponent: function () {
        var me = this;

        me.title = {
            text: esapp.Utils.getTranslation('create_account'),  // 'Create an Account',
            cls: 'fontsize20'
        };

        me.items = [{
            xtype: 'form',
            url:'register',

            bodyPadding: '5 15 5 5',

            fieldDefaults: {
                msgTarget: 'qtip',
                autoFitErrors: false,
                height: 40,
                width: '100%',
                fieldCls: 'fontsize20'
                //labelCls: 'fontsize20',
                //labelSeparator: '',
                //labelAlign: 'right',
                //labelWidth: 120,
                //minWidth: 400,
            },

            buttonAlign: 'center',
            buttons: [{
                text: '<b style="font-size: 20px">' + esapp.Utils.getTranslation('register') + '</b>',  // 'Register'
                disabled: true,
                formBind: true,
                iconAlign: 'left',
                iconCls: 'fa fa-user-plus fa-lg',
                style: { color: 'black' },
                // glyph: 'xf0c7@FontAwesome',
                scale: 'medium',
                width: '50%',
                handler: function(){
                    var form = this.up('form'); // get the form panel
                    if (form.isValid()) { // make sure the form contains valid data before submitting
                        form.submit({
                            success: function(form, action) {
                                var logindata = {
                                    username: me.lookupReference('user').value,
                                    password: me.lookupReference('pass').value
                                }
                                esapp.login(logindata);
                                me.close();
                            },
                            failure: function(form, action) {

                            }
                        });
                    }
                }
            }],


            defaults: {
                padding: '5 5 5 5',
                allowBlank: false,
                hideLabel: true,
                listeners: {
                    afterrender: function (me) {
                        // Register the new tip with an element's ID
                        Ext.tip.QuickTipManager.register({
                            target: me.getId(), // Target ID
                            title: '',  // QuickTip Header
                            text: me.emptyText, // Tip content
                            autoShow: true,
                            trackMouse: false
                        });
                    }
                }
            },
            items: [{
                xtype: 'textfield',
                name: 'fullname',
                //fieldLabel: 'Full Name',
                emptyText: esapp.Utils.getTranslation('fullname')   // 'Full Name'
                //ui: 'light'
            },{
                xtype: 'textfield',
                name: 'user',
                reference: 'user',
                //fieldLabel: 'Username',
                emptyText: esapp.Utils.getTranslation('username'),   // 'Username',
                validator: function(value){
                    if (value.length > 3){
                        if (me.getViewModel().getStore('users').findRecord('userid', value) != null){
                            return esapp.Utils.getTranslation('username_already_exists');  // 'Username already exists!';
                        }
                        else return true;
                    }
                    else return true;
                }
                //vtypeText: 'Username already exists!'
                //enableKeyEvents: true,
                //, listeners:{
                //    keyup:function(field, event){
                //        if (field.length > 3){
                //            // Search in user store if username/userid already exists.
                //            field.validate();
                //        }
                //        if(event.getKey() >= 65 && event.getKey() <= 90) {
                //           //the key was A-Z
                //        }
                //        if(event.getKey() >= 97 && event.getKey() <= 122) {
                //           //the key was a-z
                //        }
                //    }
                //}
            },{
                xtype: 'textfield',
                name: 'email',
                //fieldLabel: 'Email',
                emptyText: esapp.Utils.getTranslation('email'),   // 'Email',
                vtype: 'email'
            },{
                xtype: 'textfield',
                name: 'pass',
                itemId: 'pass',
                reference: 'pass',
                //fieldLabel: 'Password',
                emptyText: esapp.Utils.getTranslation('password'),   // 'Password',
                inputType: 'password',
                listeners: {
                    validitychange: function(field){
                        field.next().validate();
                    },
                    blur: function(field){
                        field.next().validate();
                    }
                }
            },{
                xtype: 'textfield',
                name: 'pass-cfrm',
                //fieldLabel: 'Verify',
                emptyText: esapp.Utils.getTranslation('verify_password'),   // 'Verify password',
                inputType: 'password',
                vtype: 'password',
                initialPassField: 'pass' // id of the initial password field
            }]
        }];

        me.callParent();
    }
});
