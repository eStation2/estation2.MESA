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
        },

        fieldExists: function(o){return typeof o != 'undefined' && o != null},   // && o.trim()!='';

        objectExists: function (o){return typeof o != 'undefined' && o != null;},

        is_array: function (input){return typeof(input)=='object'&&(input instanceof Array);},

        RGBtoHex: function (R,G,B) {return "#"+this.toHex(R)+this.toHex(G)+this.toHex(B)},
        //function RGBToHex(rgb) {
        //var char = "0123456789ABCDEF";
        //return String(char.charAt(Math.floor(rgb / 16))) + String(char.charAt(rgb - (Math.floor(rgb / 16) * 16)));
        //}

        toHex: function (N) {
             if (N==null) return "00";
             N=parseInt(N); if (N==0 || isNaN(N)) return "00";
             N=Math.max(0,N); N=Math.min(N,255); N=Math.round(N);
             return "0123456789ABCDEF".charAt((N-N%16)/16)
                  + "0123456789ABCDEF".charAt(N%16);
        },

        HexToRGB: function (hexvalue){
            function HexToR(h) { return parseInt((cutHex(h)).substring(0,2),16) }
            function HexToG(h) { return parseInt((cutHex(h)).substring(2,4),16) }
            function HexToB(h) { return parseInt((cutHex(h)).substring(4,6),16) }
            function cutHex(h) { return (h.charAt(0)=="#") ? h.substring(1,7) : h}

            if(String(hexvalue).charAt(0)!="#")
                return hexvalue;

            var R=HexToR(hexvalue);
            var G=HexToG(hexvalue);
            var B=HexToB(hexvalue);
            return R + ',' + G + ',' + B;
        },

        convertRGBtoHex: function(color){
            if (color.charAt(0) != "#") { // convert RBG to HEX if RGB value is given. Highcharts excepts only HEX.
                var rgbarray = [];
                if (this.is_array(color)) {
                    rgbarray = color;
                }
                else {
                    rgbarray = color.split(" "); // toString().replace(/,/g,' ');
                }

                var tsR = rgbarray[0];
                var tsG = rgbarray[1];
                var tsB = rgbarray[2];
                color = this.RGBtoHex(tsR, tsG, tsB);
            }
            return color;
        },

        invertHexToRGB: function (hexvalue){
            if(hexvalue.charAt(0)!="#")
                var RGB = hexvalue.split(',');
            else
                var RGB = this.HexToRGB(hexvalue).split(',');

            var R = RGB[0];
            var G = RGB[1];
            var B = RGB[2];
            var Rinverse = (R ^ 128);
            var Ginverse = (G ^ 128);
            var Binverse = (B ^ 128);
            return this.RGBtoHex(Rinverse,Ginverse,Binverse);
        }
    }
});


Ext.define('Ext.ux.ColorPicker', {
    extend : 'Ext.form.field.Picker',
    xtype: 'mycolorpicker',
    render_to: '',

    createPicker: function(){
        var me = this;

        me.picker = Ext.create('Ext.picker.Color', {
            ownerCt: this,
            renderTo:  this.up().up().up().getEl(),  //document.body,
            floating: true,
            hidden: false,
            focusOnShow: true,
            listeners: {
                select: function(field, value){
                    me.setValue('#' +value);
                    me.collapse();
                    me.picker.hide();
                },
                show: function(field,opts){
                    field.getEl().monitorMouseLeave(500, field.hide, field);
                }
            },

            // Workaround for EXTJS-14910 (5.0.1.1255)
            initEvents: function(){
                var me = this;
                me.el.on({
                    mousedown: function(e){e.preventDefault();}
                });
            }

        });
        me.picker.alignTo(me.inputEl, 'tl-bl?');
        me.picker.show(me.inputEl);

        return me.picker
    }
})


Ext.define('Ext.ux.ColorPickerCombo', {
        extend: 'Ext.form.field.Text', // 'Ext.form.field.Trigger',
        alias: 'widget.colorcbo',
        xtype: 'colorcbo',
        triggerTip: 'Please select a color.',
        picker: null,
        triggers: {
            foo: {
                //cls: 'my-foo-trigger',
                handler: this.onTriggerClick
            }
            //bar: {
            //    cls: 'my-bar-trigger',
            //    handler: function() {
            //        console.log('bar trigger clicked');
            //    }
            //}
        },
        onTriggerClick: function() {
                var me = this;
                if(!me.picker || me.picker.hidden == true) {
                        me.picker = Ext.create('Ext.picker.Color', {
                                pickerField: this,
                                ownerCt: this,
                                renderTo: document.body,
                                floating: true,
                                hidden: false,
                                focusOnShow: true,
                                style: {
                                        backgroundColor: "#fff"
                                } ,
                                listeners: {
                                        scope:this,
                                        select: function(field, value, opts){
                                                me.setValue('#' + value);
                                                me.inputEl.setStyle({backgroundColor:value});
                                                me.picker.hide();
                                        },
                                        show: function(field,opts){
                                                field.getEl().monitorMouseLeave(500, field.hide, field);
                                        },
                                }
                        });
                        me.picker.alignTo(me.inputEl, 'tl-bl?');
                        me.picker.show(me.inputEl);
                }
                else {
                        me.picker.hide();
                }
        },
});