Ext.define("esapp.view.widgets.ServiceMenuButton",{
    "extend": "Ext.button.Split",
    "controller": "widgets-servicemenubutton",
    "viewModel": {
        "type": "widgets-servicemenubutton"
    },
    xtype: "servicemenubutton",

    requires: [
        'esapp.view.widgets.ServiceMenuButtonModel',
        'esapp.view.widgets.ServiceMenuButtonController',

        'Ext.menu.Menu'
    ],

    iconCls: 'fa fa-cog fa-2x', // fa-spin 'icon-play', // icomoon fonts
    style: { color: 'gray' },
    // glyph: 'xf0c7@FontAwesome',
    scale: 'medium',

    service: null,
    text: null,
    handler: null,

    initComponent: function () {
        var me = this;

        me.name =  me.service + 'btn';
        //me.handler = 'checkStatusServices';

        me.menu = Ext.create('Ext.menu.Menu', {
            width: 100,
            margin: '0 0 10 0',
            floating: true,  // usually you want this set to True (default)
            collapseDirection: 'left',
            items: [
                // these will render as dropdown menu items when the arrow is clicked:
                {   text: 'Run',
                    name: 'run' + me.service,
                    service: me.service,
                    task: 'run',
                    // iconCls: 'fa-play-circle-o', // xf01d   // fa-play xf04b
                    glyph: 'xf04b@FontAwesome',
                    cls:'menu-glyph-color-green',
                    // style: { color: 'green' },
                    handler: 'execServiceTask'
                },
                {   text: 'Stop',
                    name: 'stop'+ me.service,
                    service: me.service,
                    task: 'stop',
                    // iconCls: 'fa fa-stop',
                    glyph: 'xf04d@FontAwesome',
                    cls:'menu-glyph-color-red',
                    // style: { color: 'red' },
                    handler: 'execServiceTask'
                },
                {   text: 'Restart',
                    name: 'restart'+ me.service,
                    service: me.service,
                    task: 'restart',
                    // iconCls: 'fa fa-refresh',
                    glyph: 'xf021@FontAwesome',
                    cls:'menu-glyph-color-orange',
                    // style: { color: 'orange' },
                    handler: 'execServiceTask'
                }
            ]
        });

        me.callParent();
    }
});
