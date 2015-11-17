Ext.define('esapp.view.acquisition.selectMapsetForIngestController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.acquisition-selectmapsetforingest',

    loadMapsetStore: function(){
        var me = this.getView(),
            mapsetsStore = this.getStore('mapsets');

        mapsetsStore.load({
            params: {
                productcode: me.productcode,
                version: me.productversion,
                subproductcode: me.subproductcode
            }
        });
    },
    mapsetItemClick: function(dataview, record ){

        this.lookupReference('savemapsetbtn').enable();
        this.getView().selectedmapset = record.get('mapsetcode');
    },
    onClose: function(win, ev) {
        var me = this.getView(),
            ref = 'savemapsetbtn',  // this.reference,
            refHolder = me.lookupReferenceHolder();
        if (refHolder) delete refHolder.getView().refs[ref];
        Ext.destroy(me);

        //win.close();
        //var me = this.getView();
        //Ext.destroy(me);
        //if (win.changesmade){
        //    Ext.data.StoreManager.lookup('ProductsActiveStore').load();
        //}
    }
});
