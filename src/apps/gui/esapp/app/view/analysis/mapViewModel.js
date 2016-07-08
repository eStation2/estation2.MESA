Ext.define('esapp.view.analysis.mapViewModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-mapview',

    stores: {
        layers: {
            source:'LayersStore'

            //model: 'esapp.model.Layer'
            //,session: true
            ////,autoLoad: true
            ////,loadMask: false
            //
            ////,sorters: {property: 'order_index', direction: 'DESC'}
            //
            //,listeners: {
            //    write: function(store, operation){
            //        Ext.toast({ html: operation.getResultSet().message, title: operation.action, width: 300, align: 't' });
            //    }
            //}
        }
    }

});
