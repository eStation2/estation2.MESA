/**
 * Created by tklooju on 6/26/2015.
 */

// Add the additional 'advanced' VTypes
Ext.apply(Ext.form.field.VTypes, {
    daterange: function(val, field) {
        var date = field.parseDate(val);

        if (!date) {
            return false;
        }
        if (field.startDateField && (!this.dateRangeMax || (date.getTime() != this.dateRangeMax.getTime()))) {
            var start = field.up('form').down('#' + field.startDateField);
            start.setMaxValue(date);
            start.validate();
            this.dateRangeMax = date;
        }
        else if (field.endDateField && (!this.dateRangeMin || (date.getTime() != this.dateRangeMin.getTime()))) {
            var end = field.up('form').down('#' + field.endDateField);
            end.setMinValue(date);
            end.validate();
            this.dateRangeMin = date;
        }
        /*
         * Always return true since we're only using this vtype to set the
         * min/max allowed values (these are tested for after the vtype test)
         */
        return true;
    }
    ,daterangeText: 'Start date must be less than end date'


    ,password: function(val, field) {
        if (field.initialPassField) {
            var pwd = field.up('form').down('#' + field.initialPassField);
            return (val == pwd.getValue());
        }
        return true;
    }
    ,passwordText: 'Passwords do not match'


    ,GeoJSON:  function(v) {
        v = v.replace(/^\s|\s$/g, ""); //trims string
        if (v.match(/([^\/\\]+)\.(geojson)$/i) )
            return true;
        else
            return false;
    }
    ,GeoJSONText: esapp.Utils.getTranslation('vtype_geojson')    // 'Must be a .geojson file.'


    ,JSON:  function(v) {
        v = v.replace(/^\s|\s$/g, ""); //trims string
        if (v.match(/([^\/\\]+)\.(json)$/i) )
            return true;
        else
            return false;
    }
    ,JSONText: esapp.Utils.getTranslation('vtype_json')    // 'Must be a .json file.'

   ,imagefile:  function(v) {
       v = v.replace(/^\s|\s$/g, ""); //trims string
       if (v.match(/([^\/\\]+)\.(gif|png|jpg|jpeg)$/i) )
           return true;
       else
           return false;
   }
   ,imagefileText: esapp.Utils.getTranslation('vtype_imagefile')    // 'Must be a .gif, .png, .jpg or .jpeg file.'

    // custom Vtype for vtype:'IPAddress'
    ,IPAddress:  function(v) {
        return /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(v);
    }
    ,IPAddressText: esapp.Utils.getTranslation('vtypeipaddress')  // 'Must be a numeric IP address',
    ,IPAddressMask: /[\d\.]/i


    // custom Vtype for vtype:'Netmask'
    ,IPNetmask:  function(v) {
        //return /^(128|192|224|24[08]|25[245].0.0.0)|(255.(0|128|192|224|24[08]|25[245]).0.0)|(255.255.(0|128|192|224|24[08]|25[245]).0)|(255.255.255.(0|128|192|224|24[08]|252))$/.test(v);
        // return /(^(128|192|224|24[08]|25[245])\.0\.0\.0$)|(^255\.(0|128|192|224|24[08]|25[245])\.0\.0$)|(^255\.255\.(0|128|192|224|24[08]|25[245])\.0$)|(^255\.255\.255\.(0|128|192|224|24[08]|252)$)/.test(v);
        return /^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})([/]([0-9]|[0-2][0-9]|3[0-2]))$/.test(v);
    }
    ,IPNetmaskText: esapp.Utils.getTranslation('vtypeipnetmask')  // 'Must be like 192.168.0.0/24'
    ,IPNetmaskMask: /[/.0-9]/


    //Here is a vType that verifies a proper directory location with a required trailing slash:
    //Matches Win and Mac OS paths: x:\foo\bar\, \\foo\bar\, /foo/bar/
    ,directory:  function(v) {
        return /^(([a-zA-Z]:){0,1}(\\|\/){1})(([-_.a-zA-Z0-9\\\/ ]+)(\\|\/){1})+$/.test(v);
    }
    ,directoryText: esapp.Utils.getTranslation('vtypedirectory')  // "This must be a valid directory location."
    ,directoryMask: /[-_.a-zA-Z0-9\\\/: ]/
});


//// custom Vtype for vtype:'IPAddress'
//Ext.apply(Ext.form.field.VTypes, {
//    IPAddress:  function(v) {
//        return /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(v);
//    },
//    IPAddressText: esapp.Utils.getTranslation('vtypeipaddress'),  // 'Must be a numeric IP address',
//    IPAddressMask: /[\d\.]/i
//});


//// custom Vtype for vtype:'Netmask'
//Ext.apply(Ext.form.field.VTypes, {
//    IPNetmask:  function(v) {
//        //return /^(128|192|224|24[08]|25[245].0.0.0)|(255.(0|128|192|224|24[08]|25[245]).0.0)|(255.255.(0|128|192|224|24[08]|25[245]).0)|(255.255.255.(0|128|192|224|24[08]|252))$/.test(v);
//        // return /(^(128|192|224|24[08]|25[245])\.0\.0\.0$)|(^255\.(0|128|192|224|24[08]|25[245])\.0\.0$)|(^255\.255\.(0|128|192|224|24[08]|25[245])\.0$)|(^255\.255\.255\.(0|128|192|224|24[08]|252)$)/.test(v);
//        return /^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})([/]([0-9]|[0-2][0-9]|3[0-2]))$/.test(v);
//    },
//    IPNetmaskText: esapp.Utils.getTranslation('vtypeipnetmask')  // 'Must be like 192.168.0.0/24'
//    ,IPNetmaskMask: /[/.0-9]/
//});


////Here is a vType that verifies a proper directory location with a required trailing slash:
////Matches Win and Mac OS paths: x:\foo\bar\, \\foo\bar\, /foo/bar/
//Ext.form.VTypes["directory"]=function(v){
// return /^(([a-zA-Z]:){0,1}(\\|\/){1})(([-_.a-zA-Z0-9\\\/ ]+)(\\|\/){1})+$/.test(v);
//};
//Ext.form.VTypes["directoryText"]=esapp.Utils.getTranslation('vtypedirectory');  // "This must be a valid directory location."
//Ext.form.VTypes["directoryMask"]=/[-_.a-zA-Z0-9\\\/: ]/;


//Ext.apply(Ext.form.VTypes, {
//    GeoJSON:  function(v) {
//        v = v.replace(/^\s|\s$/g, ""); //trims string
//        if (v.match(/([^\/\\]+)\.(geojson)$/i) )
//            return true;
//        else
//            return false;
//    },
//    GeoJSONText: esapp.Utils.getTranslation('vtype_geojson')    // 'Must be a .geojson file.'
//});

//Ext.apply(Ext.form.field.VTypes, {
//    imagefile:  function(v) {
//        v = v.replace(/^\s|\s$/g, ""); //trims string
//        if (v.match(/([^\/\\]+)\.(bmp|gif|png|jpg|jpeg)$/i) )
//            return true;
//        else
//            return false;
//    },
//    imagefileText: 'Must be like 192.168.0.0/24',
//    NetmaskMask: /[.0-9]/
//});