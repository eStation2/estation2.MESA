Ext.define('esapp.view.analysis.timeseriesChartViewModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-timeserieschartview',
    stores: {
        chartproperties: {
            model: 'esapp.model.ChartProperties',
            autoLoad: false,
            autoSync: true,
            session: true,

            proxy: {
                type: 'rest',

                appendId: false,

                api: {
                    read: 'analysis/getchartproperties',
                    create: 'analysis/getchartproperties/create',
                    update: 'analysis/getchartproperties/update',
                    destroy: 'analysis/getchartproperties/delete'
                },
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'chartproperties'
                    ,messageProperty: 'message'
                },
                writer: {
                    type: 'json',
                    writeAllFields: true,
                    rootProperty: 'chartproperty'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        console.info('CHART PROPERTIES VIEW MODEL - REMOTE EXCEPTION - Error querying the chart properties!');
                    }
                }
            }
            ,listeners: {
                update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
                    // This event is triggered on every change made in a record!
                },
                write: function(store, operation){
                    var result = Ext.JSON.decode(operation.getResponse().responseText);
                    if (operation.success) {

                    }
                }
            }
        }
    }

});
