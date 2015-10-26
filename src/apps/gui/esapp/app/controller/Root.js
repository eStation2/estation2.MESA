/**
 * The main application controller. This is a good place to handle things like routes.
 */
Ext.define('esapp.controller.Root', {
    extend: 'Ext.app.Controller',

    // create a reference in Ext.application so we can access it from multiple functions
    init: function () {

        this.callParent(arguments);
    }
});
