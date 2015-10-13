Ext.define('esapp.view.datamanagement.sendRequestController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.datamanagement-sendrequest',

    onSendClick: function () {

    },

    onCancelClick: function () {
        Ext.destroy(this.getView());
    }
});
