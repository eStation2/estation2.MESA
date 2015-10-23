/**
 * Created by Jurriaan van 't Klooster on 6/9/2015.
 */

Ext.define('esapp.Utils', {
    requires: [
        'Ext.data.StoreManager'
    ],
    //singleton: true,
    alternateClassName: ['Utils'],
    statics: {
        getTranslation: function (label) {
            // find in store
            var i18nstore = Ext.data.StoreManager.lookup('i18nStore');
            //console.info(i18nstore);
            if (i18nstore) {
                var records = i18nstore.findRecord('label', label);
                if (records) {
                    // && records.getCount() > 0
                    //var record = records.get(0);
                    return Ext.String.htmlDecode(records.data.langtranslation);
                }
                else return label;
            }
            else return label;
        },
        download: function(config) {
            var form,
                //removeNode = download.removeNode,
                frameId = Ext.id(),

            removeNode = function(node) {
                node.onload = null;
                node.parentNode.removeChild(node);
            };

            iframe = Ext.core.DomHelper.append(document.body, {
                id: frameId,
                name: frameId,
                style: 'display:none',
                tag: 'iframe'
            }),

            inputs = paramsToInputs(config.params);

            // If the download succeeds the load event won't fire but it can in the failure case. We avoid using Ext.Element on
            // the iframe element as that could cause a leak. Similarly, the load handler is registered in such a way as to
            // avoid a closure.
            iframe.onload = function() {
                // Note we only come into here in the failure case, so you'll need to include your own failure handling
                var response = this.contentDocument.body.innerHTML;
            };

            form = Ext.DomHelper.append(document.body, {
                action: config.url,
                cn: inputs,
                method: config.method || 'GET',
                tag: 'form',
                target: frameId
            });

            form.submit();

            removeNode(form);

            // Can't remove the iframe immediately or the download won't happen, so wait for 1 minute
            Ext.defer(removeNode, 1000 * 60 * 1, null, [iframe]);

            function paramsToInputs(params) {
                var inputs = [];

                for (var key in params) {
                    var values = [].concat(params[key]);

                    Ext.each(values, function(value) {
                        inputs.push(createInput(key, value));
                    });
                }

                return inputs;
            }

            function createInput(key, value) {
                return {
                    name: Ext.htmlEncode(key),
                    tag: 'input',
                    type: 'hidden',
                    value: Ext.htmlEncode(value)
                };
            }
        }
    }
});
