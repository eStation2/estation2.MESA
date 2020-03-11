Ext.define('esapp.view.analysis.mapTemplateAdminModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-maptemplateadmin',
    stores: {
        usermaptemplates: {
            model: 'esapp.model.UserMapTemplate',
            autoLoad: false,
            autoSync: true,
            session: true,
            storeId: 'usermaptemplates',

            sorters: [{
                property: 'templatename',
                direction: 'ASC'
            }],

            proxy: {
                type: 'rest',

                appendId: false,

                //extraParams: {
                //    userid: null    // esapp.getUser().userid  // 'jurvtk'
                //},

                api: {
                    read: 'analysis/usermaptemplates',
                    create: 'analysis/usermaptemplates/create',
                    update: 'analysis/usermaptemplates/update',
                    destroy: 'analysis/usermaptemplates/delete'
                },
                reader: {
                     type: 'json'
                    ,successProperty: 'success'
                    ,rootProperty: 'usermaptemplates'
                    ,messageProperty: 'message'
                },
                writer: {
                    type: 'json',
                    writeAllFields: true,
                    rootProperty: 'usermaptemplate'
                },
                listeners: {
                    exception: function(proxy, response, operation){
                        console.info('MAP TEMPLATE VIEW MODEL - REMOTE EXCEPTION - Error querying the users map templates!');
                    }
                }
            }
            ,listeners: {
                remove: function(store, record,  index , isMove , eOpts  ){
                    //console.info(store);
                    //console.info(record);
                    //console.info(index);
                },
                update: function(store, record, operation, modifiedFieldNames, details, eOpts  ){
                    // This event is triggered on every change made in a record!
                    //console.info('record updated!');
                },
                write: function(store, operation){
                    var result = Ext.JSON.decode(operation.getResponse().responseText);
                    //console.info('Write');
                    //console.info(store);
                    //console.info(operation.getRecords()[0]);
                    if (operation.success) {
                        Ext.toast({html: operation.getRecords()[0].get('templatename') + ' ' + esapp.Utils.getTranslation('deleted'), title: esapp.Utils.getTranslation('map_tpl_deleted'), width: 300, align: 't'});   // "Map template deleted"
                    }
                }
            }
        }
    }

});
