/**
 * Created by tklooju on 6/9/2015.
 */

Ext.define('esapp.Utils', {
    //singleton: true,
    alternateClassName: ['Utils'],
    statics: {
        getTranslation: function (label) {
            // find in store
            var i18nstore = Ext.data.StoreManager.lookup('i18nStore');
            //console.info(i18nstore);
            if (i18nstore) {
                var records = i18nstore.findRecord('label', label);
                if (records) {     // && records.getCount() > 0
                    //var record = records.get(0);
                    return Ext.String.htmlDecode(records.data.langtranslation);
                }
                else return label;
            }
            else return label;
        }
    }
});