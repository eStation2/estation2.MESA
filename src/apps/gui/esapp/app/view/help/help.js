
Ext.define("esapp.view.help.help",{
    "extend": "Ext.panel.Panel",
    "controller": "help-help",
    //"viewModel": {
    //    "type": "help-help"
    //},

    xtype  : 'help',

    requires: [
        'esapp.view.help.helpController',
        //'esapp.view.help.helpModel',

        'Ext.layout.container.HBox',
        'Ext.layout.container.VBox',
        'Ext.layout.container.Center'
    ],

    title: '<span class="dashboard-header-title-style">'+esapp.Utils.getTranslation('helptitle')+'</span>',
    titleAlign: 'center',
    header: {
        cls: 'dashboard-header-style'
    },

    width: 1150,
    //height: 650,
    autoHeight: true,

    layout: {
        type: 'vbox',
        pack: 'start'
        ,align: 'stretch'
    },
    frame: false,
    border: false,
    bodyPadding: '20 30 30 30',

    bodyCls: 'help-main',

    initComponent: function () {
        var me = this;

        me.setViewModel({
            "type": "help-help"
        });

        me.title = '<span class="dashboard-header-title-style">'+esapp.Utils.getTranslation('helptitle')+'</span>';

        me.items = [{
            xtype: 'dataview',
            cls: 'help-dataview',

            bind: '{documentation}',

            itemSelector: 'div.thumb-wrap',

            listeners: {
                //itemclick: 'onDocumentClick'
            },

            tpl: [
                '<tpl for=".">',
                // Break every four dataviews
                '<tpl if="xindex % 10 === 1">',
                '<div class="statement-type">{type}</div>',
                '</tpl>',
                '<div class="thumb-wrap">',
                '<a class="thumb" href="{url}" target="_blank">',
                '<div class="thumb-{thumb}"></div>',
                '<div class="thumb-title-container">',
                '<div class="thumb-title">{title}</div>',
                '<div class="thumb-title-small">'+esapp.Utils.getTranslation('uploaded')+': {uploaded}</div>',
                '</div>',
                '<div class="thumb-download"></div>',
                '</a>',
                '</div>',
                '</tpl>'
            ]
        },{
            xtype: 'dataview',
            cls: 'help-dataview',

            bind: '{weblinks}',

            itemSelector: 'div.thumb-wrap',

            listeners: {
                //itemclick: 'onDocumentClick'
            },

            tpl: [
                '<tpl for=".">',
                // Break every four dataviews
                '<tpl if="xindex % 10 === 1">',
                '<div class="statement-type">{type}</div>',
                '</tpl>',
                '<div class="thumb-wrap">',
                '<a class="thumb" href="{url}" target="_blank">',
                '<div class="thumb-{thumb}"></div>',
                '<div class="thumb-title-container">',
                '<div class="thumb-title">{title}</div>',
                '<div class="thumb-title-small">'+esapp.Utils.getTranslation('description')+': {description}</div>',
                '</div>',
                '<div class="thumb-gotolink"></div>',
                '</a>',
                '</div>',
                '</tpl>'
            ]
        },{
            xtype: 'dataview',
            cls: 'help-dataview',

            bind: '{notes}',

            itemSelector: 'div.thumb-wrap',

            listeners: {
                //itemclick: 'onDocumentClick'
            },

            tpl: [
                '<tpl for=".">',
                // Break every four dataviews
                '<tpl if="xindex % 10 === 1">',
                '<div class="statement-type">{type}</div>',
                '</tpl>',
                '<div class="thumb-wrap">',
                '<a class="thumb" href="{url}" target="_blank">',
                '<div class="thumb-{thumb}"></div>',
                '<div class="thumb-title-container">',
                '<div class="thumb-title">{title}</div>',
                '<div class="thumb-title-small">'+esapp.Utils.getTranslation('uploaded')+': {uploaded}</div>',
                '</div>',
                '<div class="thumb-download"></div>',
                '</a>',
                '</div>',
                '</tpl>'
            ]
        }];

        me.callParent();
    }
});
