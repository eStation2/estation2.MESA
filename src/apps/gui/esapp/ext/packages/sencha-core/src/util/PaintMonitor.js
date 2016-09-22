/**
 *
 */
Ext.define('Ext.util.PaintMonitor', {
    requires: [
        'Ext.util.paintmonitor.CssAnimation',
        'Ext.util.paintmonitor.OverflowChange'
    ],

    constructor: function(config) {
        return new Ext.util.paintmonitor.CssAnimation(config);
    }
});
