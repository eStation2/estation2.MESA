Ext.define('esapp.view.acquisition.product.MapsetAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-product-mapsetadmin',
    stores: {
        mapsets: {
            source: 'MapsetsStore'
        },
        mapsetsforingest: {
            model: 'esapp.model.MapSetForIngest',
            autoLoad: false,
            session: true,

            proxy: {
                type : 'ajax',
                url : 'getmapsetsforingest',
                //extraParams:{
                //    productcode: this.productcode,
                //    version: this.productversion,
                //    subproductcode: this.subproductcode
                //},
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'mapsets'
                    ,messageProperty: 'message'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                        console.info('MAPSET VIEW MODEL - REMOTE EXCEPTION - Reload the select mapset for ingest window!');

                        //Ext.Msg.show({
                        //    title: 'MAPSET VIEW MODEL- REMOTE EXCEPTION',
                        //    msg: operation.getError(),
                        //    icon: Ext.Msg.ERROR,
                        //    buttons: Ext.Msg.OK
                        //});
                    }
                }
            }
        }
    }

});
