
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

    title: esapp.Utils.getTranslation('logviewer'),     // 'Log viewer',
    header: {
        titlePosition: 0,
        titleAlign: 'center'
    },

    constrainHeader: true,
    //constrain: true,
    modal: true,
    closable: true,
    closeAction: 'destroy', // 'hide',
    resizable: true,
    autoScroll:true,
    maximizable: false,
    width:800,
    height: Ext.getBody().getViewSize().height < 625 ? Ext.getBody().getViewSize().height-10 : 800,  // 600,
    maxHeight: 800,

    border:true,
    frame:true,
    layout: {
        type  : 'fit',
        padding: 5
    },

    params: {
       logtype: null,
       record: null
    },

    listeners: {
        beforerender: "getFile"
    },

    initComponent: function () {
        var me = this;

        //me.id = 'logviewer' + me.params.logtype + me.params.record.get('productid');

        me.title = esapp.Utils.getTranslation('logviewer');     // 'Log viewer',

        me.tbar = ['  ',
            {
                xtype: 'textfield',
                id:'highlightfindstring', // + me.logtype + me.params.record.get('productid'),
                fieldLabel: esapp.Utils.getTranslation('search'),    // 'Search',
                labelWidth: 60,
                labelAlign: 'left',
                labelStyle: 'font-weight:bold;',
                hidden:false,
                qtip: esapp.Utils.getTranslation('tiplogviewsearch'),    // 'Search and highlight in current file.',
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
            },'->', // same as { xtype: 'tbfill' }
            {
                xtype: 'button',
                iconCls: 'fa fa-refresh fa-2x',
                style: { color: 'gray' },
                enableToggle: false,
                scale: 'medium',
                handler: 'getFile'
            }
        ];

        me.items = [{
            xtype: 'htmleditor',
            id: 'logfilecontent', // + me.logtype + me.params.record.get('productid'),
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
