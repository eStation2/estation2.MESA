Ext.define('esapp.view.acquisition.selectMapsetForIngestModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.acquisition-selectmapsetforingest',
    stores: {
        mapsets: {
            model: 'esapp.model.MapSet',
            autoLoad: false,
            session: true,

            proxy: {
                type : 'ajax',
                url : 'getmapsets',
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
                        Ext.Msg.show({
                            title: 'MAPSET MODEL- REMOTE EXCEPTION',
                            msg: operation.getError(),
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                }
            }
        }
    }

});
