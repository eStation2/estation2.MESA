// http://www.sencha.com/forum/showthread.php?290747
// https://github.com/JarvusInnovations/sencha-hotfixes/blob/master/jarvus-hotfixes-ext-5.0.1.1255/overrides/grid/plugin/BufferedRenderer/BoxReadyViewRefreshArgs.js
Ext.define('esapp.overrides.grid.plugin.BufferedRenderer.BoxReadyViewRefreshArgs', {
    override: 'Ext.grid.plugin.BufferedRenderer',
//    compatibility: '5.0.1255',

    onViewRefresh: function(view, records) {
        var me = this,
            rows = view.all,
            oldScrollHeight = me.scrollHeight,
            height,
            scrollHeight;

        // Recheck the variability of row height in the view.
        me.checkVariableRowHeight();

        // The first refresh on the leading edge of the initial layout will mean that the
        // View has not had the sizes of flexed columns calculated and flushed yet.
        // So measurement of DOM height for calculation of an approximation of the variableRowHeight would be premature.
        if (me.variableRowHeight && !view.componentLayoutCounter) {
            view.on({
                boxready: function() {
                    me.onViewRefresh(view, records);
                },
                single: true
            });
            return;
        }

        // View has rows, delete the rowHeight property to trigger a recalculation when scrollRange is calculated
        if (!view.hasOwnProperty('rowHeight') && rows.getCount()) {
            // We need to calculate the table size based upon the new viewport size and current row height
            // It tests hasOwnProperty so must delete the property to make it recalculate.
            delete me.rowHeight;
        }

        // Calculates scroll range. Also calculates rowHeight if we do not have an own rowHeight property.
        // That will be the case if the view contains some rows.
        scrollHeight = me.getScrollHeight();

        if (scrollHeight != oldScrollHeight) {
            me.stretchView(view, scrollHeight);
        }

        // If we are instigating the refresh, we must only update the stretcher.
        if (me.refreshing) {
            return;
        }

        if (me.scrollTop !== view.getScrollY()) {
            // The view may have refreshed and scrolled to the top, for example
            // on a sort. If so, it's as if we scrolled to the top, so we'll simulate
            // it here.
            me.onViewScroll();
        } else {
            if (!me.hasOwnProperty('bodyTop')) {
                me.bodyTop = rows.startIndex * me.rowHeight;
                view.setScrollY(me.bodyTop);
            }
            me.setBodyTop(me.bodyTop);

            // With new data, the height may have changed, so recalculate the rowHeight and viewSize.
            // This will either add or remove some rows.
            height = view.getHeight();
            if (rows.getCount() && height > 0) {
                me.onViewResize(view, null, height);

                // If we repaired the view by adding or removing records, then keep the records array
                // consistent with what is there for subsequent listeners.
                // For example the WidgetColumn listener which postprocesses all rows: https://sencha.jira.com/browse/EXTJS-13942
                if (records && (rows.getCount() !== records.length)) {
                    records.length = 0;
                    records.push.apply(records, me.store.getRange(rows.startIndex, rows.endIndex));
                }
            }
        }
    }
});

//Ext.define('esapp.overrides.grid.plugin.BufferedRenderer', {
//    override: 'Ext.grid.plugin.BufferedRenderer',
//
//    //listen to panel show to refresh
//    init: function(grid) {
//        var me = this;
//        me.callParent(arguments);
//        me.grid.on('show', me.onViewRefresh, me);
//    },
//
//    //if it is hidden do nothing
//    onViewRefresh: function() {
//        if(this.grid.isHidden()) return;
//        this.callParent(arguments);
//    },
//
//    //release the listener made on the override
//    destroy: function() {
//        var me = this,
//            grid = me.grid;
//
//
//        if (grid) {
//            grid.un('show', me.onViewRefresh, me);
//        }
//        this.callParent(arguments);
//    }
//});