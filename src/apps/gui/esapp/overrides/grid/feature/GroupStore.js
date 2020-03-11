/**
 * Created by tklooju on 9/6/2016.
 */
/** */
Ext.define('Ext.overrides.grid.feature.GroupStore', {
    override: 'Ext.grid.feature.GroupStore',

    indexOf: function(record) {
        var ret = -1;
        // Jurvtk: Added record && to resolve bug Uncaught TypeError: Cannot read property 'isCollapsedPlaceholder' of undefined
        // with grid group feature and grid widgetcolumn containing a grid as a widget.
        if (record && !record.isCollapsedPlaceholder) {
            ret = this.data.indexOf(record);
        }
        return ret;
    }
});