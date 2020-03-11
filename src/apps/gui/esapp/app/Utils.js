/**
 * Created by Jurriaan van 't Klooster on 6/9/2015.
 */

Ext.define('esapp.Utils', {
    singleton:true,
    uses: [
        'Ext.data.StoreManager'
    ],
    //alternateClassName: ['Utils'],

    //privates: {

	/**
	 * Shows Message Box with error
	 * @param {String} msg Message to show
	 * @param {String} title Optional. Title for message box (defaults to Error)
	 */
	showError:function(msg, title) {
		title = title || esapp.Utils.getTranslation('error'); // 'Error'
		Ext.Msg.show({
			title:title,
			msg:msg,
			modal:true,
			icon:Ext.Msg.ERROR,
			buttons:Ext.Msg.OK
		});
	}, // eo function showError

    makeGridJSON: function (store){
        var data = new Array();
        var records = store.getRange();
        for (var i = 0; i < records.length; i++) {
            data.push(records[i].data);
        }
        return Ext.util.JSON.encode(data);
    },

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

    union_arrays: function (x, y) {
      var obj = {};
      for (var i = x.length-1; i >= 0; -- i)
         obj[x[i]] = x[i];
      for (var i = y.length-1; i >= 0; -- i)
         obj[y[i]] = y[i];
      var res = []
      for (var k in obj) {
        if (obj.hasOwnProperty(k))  // <-- optional
          res.push(obj[k]);
      }
      return res;
    },

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
    },

    colorrenderer: function(color) {
        var renderTpl = color;

        if (color.trim()==''){
            renderTpl = 'transparent';
        }
        else {
            renderTpl = '<span style="background:rgb(' + esapp.Utils.HexToRGB(color) + '); color:' + esapp.Utils.invertHexToRGB(color) + ';">' + esapp.Utils.HexToRGB(color) + '</span>';
        }
        return renderTpl;
    },

    sleepFor: function(sleepDuration){
        var now = new Date().getTime();
        while(new Date().getTime() < now + sleepDuration){ /* do nothing */ }
    },

    hasClass: function (ele,cls) {
        return ele.className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));
    },

    addClass: function (ele,cls) {
        if (!this.hasClass(ele,cls)) ele.className += " "+cls;
    },

    removeClass: function (ele,cls) {
        if (this.hasClass(ele,cls)) {
            var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
            ele.className=ele.className.replace(reg,' ');
        }
    }

    //,md5cycle: function (x, k) {
    //    var a = x[0], b = x[1], c = x[2], d = x[3];
    //
    //    a = this.ff(a, b, c, d, k[0], 7, -680876936);
    //    d = this.ff(d, a, b, c, k[1], 12, -389564586);
    //    c = this.ff(c, d, a, b, k[2], 17,  606105819);
    //    b = this.ff(b, c, d, a, k[3], 22, -1044525330);
    //    a = this.ff(a, b, c, d, k[4], 7, -176418897);
    //    d = this.ff(d, a, b, c, k[5], 12,  1200080426);
    //    c = this.ff(c, d, a, b, k[6], 17, -1473231341);
    //    b = this.ff(b, c, d, a, k[7], 22, -45705983);
    //    a = this.ff(a, b, c, d, k[8], 7,  1770035416);
    //    d = this.ff(d, a, b, c, k[9], 12, -1958414417);
    //    c = this.ff(c, d, a, b, k[10], 17, -42063);
    //    b = this.ff(b, c, d, a, k[11], 22, -1990404162);
    //    a = this.ff(a, b, c, d, k[12], 7,  1804603682);
    //    d = this.ff(d, a, b, c, k[13], 12, -40341101);
    //    c = this.ff(c, d, a, b, k[14], 17, -1502002290);
    //    b = this.ff(b, c, d, a, k[15], 22,  1236535329);
    //
    //    a = this.gg(a, b, c, d, k[1], 5, -165796510);
    //    d = this.gg(d, a, b, c, k[6], 9, -1069501632);
    //    c = this.gg(c, d, a, b, k[11], 14,  643717713);
    //    b = this.gg(b, c, d, a, k[0], 20, -373897302);
    //    a = this.gg(a, b, c, d, k[5], 5, -701558691);
    //    d = this.gg(d, a, b, c, k[10], 9,  38016083);
    //    c = this.gg(c, d, a, b, k[15], 14, -660478335);
    //    b = this.gg(b, c, d, a, k[4], 20, -405537848);
    //    a = this.gg(a, b, c, d, k[9], 5,  568446438);
    //    d = this.gg(d, a, b, c, k[14], 9, -1019803690);
    //    c = this.gg(c, d, a, b, k[3], 14, -187363961);
    //    b = this.gg(b, c, d, a, k[8], 20,  1163531501);
    //    a = this.gg(a, b, c, d, k[13], 5, -1444681467);
    //    d = this.gg(d, a, b, c, k[2], 9, -51403784);
    //    c = this.gg(c, d, a, b, k[7], 14,  1735328473);
    //    b = this.gg(b, c, d, a, k[12], 20, -1926607734);
    //
    //    a = this.hh(a, b, c, d, k[5], 4, -378558);
    //    d = this.hh(d, a, b, c, k[8], 11, -2022574463);
    //    c = this.hh(c, d, a, b, k[11], 16,  1839030562);
    //    b = this.hh(b, c, d, a, k[14], 23, -35309556);
    //    a = this.hh(a, b, c, d, k[1], 4, -1530992060);
    //    d = this.hh(d, a, b, c, k[4], 11,  1272893353);
    //    c = this.hh(c, d, a, b, k[7], 16, -155497632);
    //    b = this.hh(b, c, d, a, k[10], 23, -1094730640);
    //    a = this.hh(a, b, c, d, k[13], 4,  681279174);
    //    d = this.hh(d, a, b, c, k[0], 11, -358537222);
    //    c = this.hh(c, d, a, b, k[3], 16, -722521979);
    //    b = this.hh(b, c, d, a, k[6], 23,  76029189);
    //    a = this.hh(a, b, c, d, k[9], 4, -640364487);
    //    d = this.hh(d, a, b, c, k[12], 11, -421815835);
    //    c = this.hh(c, d, a, b, k[15], 16,  530742520);
    //    b = this.hh(b, c, d, a, k[2], 23, -995338651);
    //
    //    a = this.ii(a, b, c, d, k[0], 6, -198630844);
    //    d = this.ii(d, a, b, c, k[7], 10,  1126891415);
    //    c = this.ii(c, d, a, b, k[14], 15, -1416354905);
    //    b = this.ii(b, c, d, a, k[5], 21, -57434055);
    //    a = this.ii(a, b, c, d, k[12], 6,  1700485571);
    //    d = this.ii(d, a, b, c, k[3], 10, -1894986606);
    //    c = this.ii(c, d, a, b, k[10], 15, -1051523);
    //    b = this.ii(b, c, d, a, k[1], 21, -2054922799);
    //    a = this.ii(a, b, c, d, k[8], 6,  1873313359);
    //    d = this.ii(d, a, b, c, k[15], 10, -30611744);
    //    c = this.ii(c, d, a, b, k[6], 15, -1560198380);
    //    b = this.ii(b, c, d, a, k[13], 21,  1309151649);
    //    a = this.ii(a, b, c, d, k[4], 6, -145523070);
    //    d = this.ii(d, a, b, c, k[11], 10, -1120210379);
    //    c = this.ii(c, d, a, b, k[2], 15,  718787259);
    //    b = this.ii(b, c, d, a, k[9], 21, -343485551);
    //
    //    x[0] = this.add32(a, x[0]);
    //    x[1] = this.add32(b, x[1]);
    //    x[2] = this.add32(c, x[2]);
    //    x[3] = this.add32(d, x[3]);
    //
    //},
    //
    //cmn: function (q, a, b, x, s, t) {
    //    a = this.add32(this.add32(a, q), this.add32(x, t));
    //    return this.add32((a << s) | (a >>> (32 - s)), b);
    //},
    //
    //ff: function (a, b, c, d, x, s, t) {
    //    return this.cmn((b & c) | ((~b) & d), a, b, x, s, t);
    //},
    //
    //gg: function (a, b, c, d, x, s, t) {
    //    return this.cmn((b & d) | (c & (~d)), a, b, x, s, t);
    //},
    //
    //hh: function (a, b, c, d, x, s, t) {
    //    return this.cmn(b ^ c ^ d, a, b, x, s, t);
    //},
    //
    //ii: function (a, b, c, d, x, s, t) {
    //    return this.cmn(c ^ (b | (~d)), a, b, x, s, t);
    //},
    //
    //md51: function (s) {
    //    txt = '';
    //    var n = s.length,
    //    state = [1732584193, -271733879, -1732584194, 271733878], i;
    //    for (i=64; i<=s.length; i+=64) {
    //        this.md5cycle(state, this.md5blk(s.substring(i-64, i)));
    //    }
    //    s = s.substring(i-64);
    //    var tail = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0];
    //    for (i=0; i<s.length; i++)
    //    tail[i>>2] |= s.charCodeAt(i) << ((i%4) << 3);
    //    tail[i>>2] |= 0x80 << ((i%4) << 3);
    //    if (i > 55) {
    //        this.md5cycle(state, tail);
    //        for (i=0; i<16; i++) tail[i] = 0;
    //    }
    //    tail[14] = n*8;
    //    this.md5cycle(state, tail);
    //    return state;
    //},
    //
    ///* there needs to be support for Unicode here,
    // * unless we pretend that we can redefine the MD-5
    // * algorithm for multi-byte characters (perhaps
    // * by adding every four 16-bit characters and
    // * shortening the sum to 32 bits). Otherwise
    // * I suggest performing MD-5 as if every character
    // * was two bytes--e.g., 0040 0025 = @%--but then
    // * how will an ordinary MD-5 sum be matched?
    // * There is no way to standardize text to something
    // * like UTF-8 before transformation; speed cost is
    // * utterly prohibitive. The JavaScript standard
    // * itself needs to look at this: it should start
    // * providing access to strings as preformed UTF-8
    // * 8-bit unsigned value arrays.
    // */
    //md5blk: function (s) { /* I figured global was faster.   */
    //    var md5blks = [], i; /* Andy King said do it this way. */
    //    for (i=0; i<64; i+=4) {
    //    md5blks[i>>2] = s.charCodeAt(i)
    //    + (s.charCodeAt(i+1) << 8)
    //    + (s.charCodeAt(i+2) << 16)
    //    + (s.charCodeAt(i+3) << 24);
    //    }
    //    return md5blks;
    //},
    //
    //rhex: function (n)
    //{
    //    var hex_chr = '0123456789abcdef'.split('');
    //    var s='', j=0;
    //    for(; j<4; j++)
    //    s += hex_chr[(n >> (j * 8 + 4)) & 0x0F]
    //    + hex_chr[(n >> (j * 8)) & 0x0F];
    //    return s;
    //},
    //
    //hex: function (x) {
    //    for (var i=0; i<x.length; i++)
    //    x[i] = this.rhex(x[i]);
    //    return x.join('');
    //},
    //
    //md5: function (s) {
    //    return this.hex(this.md51(s));
    //},
    //
    ///* this function is much faster,
    //so if possible we use it. Some IEs
    //are the only ones I know of that
    //need the idiotic second function,
    //generated by an if clause.  */
    //
    //add32: function (a, b) {
    //    return (a + b) & 0xFFFFFFFF;
    //},
    //
    //__add32: function (x, y) {
    //    var lsw = (x & 0xFFFF) + (y & 0xFFFF),
    //    msw = (x >> 16) + (y >> 16) + (lsw >> 16);
    //    return (msw << 16) | (lsw & 0xFFFF);
    //}
    //
    ////if (md5('hello') != '5d41402abc4b2a76b9719d911017c592') {
    ////    function add32(x, y) {
    ////        var lsw = (x & 0xFFFF) + (y & 0xFFFF),
    ////        msw = (x >> 16) + (y >> 16) + (lsw >> 16);
    ////        return (msw << 16) | (lsw & 0xFFFF);
    ////    }
    ////}

    //}
});


Ext.define('Ext.ux.ColorSelector', {
    extend : 'Ext.form.field.Picker',
    xtype: 'mycolorselector',
    createPicker: function(){
        var me = this;

        me.selector = Ext.create('Ext.panel.Panel', {
             reference: 'color_selector'
            ,layout:'fit'
            ,hidden: false
            ,minWidth: 600
            ,minHeigth: 500
            ,autoShow: true
            ,closable: true
            ,closeAction: 'hide'
            ,modal: true
            ,deferredRender: false
            ,frame: false
            ,border: false
            ,collapsible: false
            ,bodyStyle: 'padding: 10px 3px 0px 3px;'
            ,cls: 'newpanelstyle'
            ,ownerCt: this
            // ,renderTo:  this.up().up().up().getEl()  //document.body,
            ,floating: true
            ,focusOnShow: true
            ,listeners: {
                 show: function(){
                     this.down('colorselector').setValue(me.value);
                 }
            }
            ,bbar: {
                padding: 4,
                defaults: {
                    scale: 'medium',
                    hidden: false
                },
                items: ['->', {
                    xtype: 'button',
                    text: esapp.Utils.getTranslation('ok'),    // 'Ok',
                    handler: function(){
                        var hexvalue = this.up().up().down('colorselector').getValue();
                        var rgbvalue = esapp.Utils.HexToRGB(hexvalue);
                        rgbvalue = rgbvalue.replace(/,/g, ' ');
                        me.setValue(hexvalue);

                        me.selector.close();
                    }
                }]
            }
            ,items: [{
                xtype: 'colorselector',
                format: "#HEX6",
                value: me.value
            }]
        });

        // me.selector.alignTo(me.inputEl, 'tl-bl?');
        // me.selector.show(me.inputEl);

        return me.selector
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
});


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
                                        }
                                }
                        });
                        me.picker.alignTo(me.inputEl, 'tl-bl?');
                        me.picker.show(me.inputEl);
                }
                else {
                        me.picker.hide();
                }
        }
});