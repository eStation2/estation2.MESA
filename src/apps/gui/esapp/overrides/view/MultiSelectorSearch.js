/**
 * Created by tklooju on 12/22/2016.
 */

Ext.define('Ext.overrides.view.MultiSelectorSearch', {
    override: 'Ext.view.MultiSelectorSearch',

    config: {
        store: null
    },

    initComponent: function() {
        var me = this, owner = me.owner, items = me.makeItems(), i, item, records, store;

        //me.dockedItems = me.makeDockedItems();
        //me.items = items;

        // REPLACE
        // store = Ext.data.StoreManager.lookup(me.store);
        store = me.store;

        for (i = items.length; i--;) {
            if ((item = items[i]).xtype === 'grid') {
                item.store = store;
                item.isSearchGrid = true;
                item.selModel = item.selModel || {
                    type: 'checkboxmodel',
                    pruneRemoved: false,
                    listeners: {
                        selectionchange: 'onSelectionChange'
                    }
                };

                Ext.merge(item, me.grid);

                if (!item.columns) {
                    item.hideHeaders = true;
                    item.columns = [
                        {
                            flex: 1,
                            dataIndex: me.field
                        }
                    ];
                }

                break;
            }
        }

        me.callParent();

        records = me.getOwnerStore().getRange();
        if (!owner.convertSelectionRecord.$nullFn) {
            for (i = records.length; i--;) {
                records[i] = owner.convertSelectionRecord(records[i]);
            }
        }

        // REPLACE
        //        if (store.isLoading() || (store.loadCount === 0 && !store.getCount())) {
        //            store.on('load', function() {
        //                if (!me.isDestroyed) {
        //                    me.selectRecords(records);
        //                }
        //            }, null, {single: true});
        //        } else {
        //            me.selectRecords(records);
        //        }
        me.initializeStore();
    },

    makeDockedItems: function () {

    },

    deselectAll: function() {
        var searchGrid = this.lookupReference('searchGrid');

        return searchGrid.getSelectionModel().deselectAll();
    },

    // NEW -> define by config and override
    setStore: function(store) {
        var oldStore = this.store;

        this.store = store;

        this.updateStore(store, oldStore);
    },


    // NEW
    updateStore: function(newValue, oldValue) {
        // <debug>
        //console.log('updateStore', this.store, newValue, oldValue);
        // </debug>

        this.initializeStore();
    },


    // NEW
    initializeStore: function() {
        var me = this, store = me.store, records;

        if (store.isStore) {
            records = me.getOwnerStore().getRange();


            if (store.isLoading() || store.loadCount === 0 && !store.getCount()) {
                store.on('load', function() {
                    if (!me.isDestroyed) {
                        me.selectRecords(records);
                    }
                }, null, {
                    single: true
                });
            }
            else {
                me.selectRecords(records);
            }

            // Update grids
            Ext.Array.each(me.query('grid'), function(grid) {
                grid.setStore(store)
            });
        }
    }
});