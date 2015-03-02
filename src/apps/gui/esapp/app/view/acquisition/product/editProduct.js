
Ext.define("esapp.view.acquisition.product.editProduct",{
    "extend": "Ext.window.Window",
    "controller": "acquisition-product-editproduct",
    "viewModel": {
        "type": "acquisition-product-editproduct"
    },
    xtype: "editproduct",

    requires: [
        'esapp.view.acquisition.product.editProductModel',
        'esapp.view.acquisition.product.editProductController'
    ],

    title: 'Layout Window with title <em>after</em> tools',
    header: {
        titlePosition: 2,
        titleAlign: 'center'
    },
    module: true,
    closable: true,
//    closeAction: 'hide',
    maximizable: true,
//    animateTarget: button,
    width: 600,
    height: 350,
    tools: [{type: 'pin'}],
    layout: {
        type: 'border',
        padding: 5
    },
    items: [{
        region: 'west',
        title: 'Navigation',
        width: 200,
        split: true,
        collapsible: true,
        floatable: false
    }, {
        region: 'center',
        xtype: 'tabpanel',
        items: [{
            // LTR even when example is RTL so that the code can be read
            rtl: false,
            title: 'Bogus Tab',
            html: '<p>Window configured with:</p><pre style="margin-left:20px"><code>header: {\n    titlePosition: 2,\n    titleAlign: "center"\n},\nmaximizable: true,\ntools: [{type: "pin"}],\nclosable: true</code></pre>'
        }, {
            title: 'Another Tab',
            html: 'Hello world 2'
        }, {
            title: 'Closable Tab',
            html: 'Hello world 3',
            closable: true
        }]
    }]

});
