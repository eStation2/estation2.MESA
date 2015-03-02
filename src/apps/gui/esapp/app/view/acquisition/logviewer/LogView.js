
Ext.define("esapp.view.acquisition.logviewer.LogView",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-logviewer-logview",
    "viewModel": {
        "type": "acquisition-logviewer-logview"
    },

    xtype: "logviewer",

    requires: [
        'esapp.view.acquisition.logviewer.LogViewController',
        'esapp.view.acquisition.logviewer.LogViewModel',

        'Ext.form.field.HtmlEditor',
        'Ext.form.field.Text',
        'Ext.layout.container.Center',
        'Ext.XTemplate'
    ],
    // id: null,

    title: 'Log viewer',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },
    modal: false,
    closable: true,
    closeAction: 'destroy', // 'hide',
    maximizable: false,
    width:1000,
    height:600,
    border:true,
    frame:true,
    layout: {
        type  : 'fit',
        padding: 5
    },
    autoScroll: true,

    params: {
       logtype: null,
       record: null
    },

    listeners: {
        beforerender: "getFile"
    },

    initComponent: function () {
        var me = this;

        //me.id = 'logviewer' + me.params.logtype + me.params.record.get('productID');

        me.tbar = ['  ',
            {
                xtype: 'textfield',
                id:'highlightfindstring', // + me.logtype + me.params.record.get('productID'),
                fieldLabel: 'Search',
                labelWidth: 60,
                labelAlign: 'left',
                labelStyle: 'font-weight:bold;',
                hidden:false,
                qtip:'Search and highlight in current file.',
                width:250
//                scope:this
//                listeners: {
//                    keyup: function(txtfield, e) {
//                             console.info(this);
//                             console.info(txtfield);
//                             console.info(e);
////                             if(Ext.EventObject.ESC == e.getKey()) {
////                                field.onTriggerClick();
////                             }
////                             else {
////                                 var val = this.getRawValue();
////                                 var re = new RegExp('.*' + val + '.*', 'i');
////                             }
//                       }
//                }
            },{
                text: '',
                iconCls: 'magnifier-left-icon',
                handler: 'highlightSearchString'
            }
        ];

        me.items = [{
            xtype: 'htmleditor',
            id: 'logfilecontent', // + me.logtype + me.params.record.get('productID'),
            autoScroll: true,
            border: true,
            frame: true,
            layout: {
                type  : 'fit',
                padding: 5
            },
            enableAlignments: false,
            enableColors: true,
            enableFont: true,
            enableFontSize: true,
            enableFormat: false,
            enableLinks: false,
            enableLists: false,
            enableSourceEdit: false
        }];

        me.callParent();

    }
});
