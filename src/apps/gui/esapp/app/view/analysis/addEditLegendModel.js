Ext.define('esapp.view.analysis.addEditLegendModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-addeditlegend',

    requires: [
        "esapp.model.LegendClasses",
        'esapp.model.LegendAssignedDataset'
    ],

    stores: {
        legendClassesStore: {
            model: 'esapp.model.LegendClasses',
            autoLoad: false,
            autoSync: false,
            session: false,

            proxy: {
                type: 'rest',

                appendId: false,
                extraParams:{
                    legendid:''
                },
                api: {
                    read: 'legends/legendclasses',
                    create: 'legends/legendclasses/create',
                    update: 'legends/legendclasses/update',
                    destroy: 'legends/legendclasses/delete'
                },
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'legendclasses'
                    ,messageProperty: 'message'
                },
                writer: {
                    type: 'json',
                    writeAllFields: true,
                    rootProperty: 'legendclasses'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        console.info('ADD EDIT LEGEND VIEW MODEL - REMOTE EXCEPTION - Error querying the legend classes!');
                    }
                }
            }
            // ,listeners: {
            //     update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
            //         // This event is triggered on every change made in a record!
            //     },
            //     write: function(store, operation){
            //         var result = Ext.JSON.decode(operation.getResponse().responseText);
            //         if (operation.success) {
            //
            //         }
            //     }
            // }
        },
        assigneddatasets: {
            model: 'esapp.model.LegendAssignedDataset',
            autoLoad: false,
            autoSync: false,
            session: true,

            proxy: {
                type: 'rest',
                appendId: false,
                extraParams:{
                    legendid:''
                },
                api: {
                    read: 'legends/assigneddatasets',
                    create: 'legends/assigneddatasets/create',
                    update: 'legends/assigneddatasets/update',
                    destroy: 'legends/assigneddatasets/delete'
                },
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'assigneddatasets'
                    ,messageProperty: 'message'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        console.info('ADD EDIT LEGEND VIEW MODEL - REMOTE EXCEPTION - Error querying the legend assigned datasets!');
                    }
                }
            }
        }
    }

});
