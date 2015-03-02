
Ext.define("esapp.view.dashboard.Connection",{
    "extend": "Ext.container.Container",
    "controller": "dashboard-connection",
    "viewModel": {
        "type": "dashboard-connection"
    },
    xtype  : 'dashboard-connection',

    layout: {
        type: 'hbox',
        pack: 'start',
        align: 'middle'
    },
    width: 100,
    margin: '0 0 0 0',
    defaults: {
        width:35
    },
    connected: true,


    initComponent: function () {
        var me = this;

        if (me.connected){

            me.items = [{
                xtype: 'image',
                glyph: 'xf0e7@FontAwesome', // 'fa-flash'
                cls:'glyph-color-green fa-rotate-270 fa-3x'
            },{
                xtype: 'image',
                glyph: 'xf0c1@FontAwesome', // 'fa-chain'
                cls:'glyph-color-green fa-flip-horizontal fa-3x'
            },{
                xtype: 'image',
                glyph: 'xf0e7@FontAwesome', // 'fa-flash'
                cls:'glyph-color-green fa-rotate-90 fa-3x'
            }];
        }
        else {
            me.items = [{
                xtype: 'image',
                glyph: 'xf0e7@FontAwesome', // 'fa-flash'
                cls:'glyph-color-red fa-rotate-270 fa-3x'
            },{
                xtype: 'image',
                glyph: 'xf127@FontAwesome', // 'fa-chain-broken'
                cls:'glyph-color-red fa-flip-horizontal fa-3x'
            },{
                xtype: 'image',
                glyph: 'xf0e7@FontAwesome', // 'fa-flash'
                cls:'glyph-color-red fa-rotate-90 fa-3x'
            }];
        }

        me.callParent();
    }

});
