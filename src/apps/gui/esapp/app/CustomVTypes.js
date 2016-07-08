/**
 * Created by tklooju on 6/26/2015.
 */

// custom Vtype for vtype:'IPAddress'
Ext.apply(Ext.form.field.VTypes, {
    IPAddress:  function(v) {
        return /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(v);
    },
    IPAddressText: esapp.Utils.getTranslation('vtypeipaddress'),  // 'Must be a numeric IP address',
    IPAddressMask: /[\d\.]/i
});


// custom Vtype for vtype:'Netmask'
Ext.apply(Ext.form.field.VTypes, {
    IPNetmask:  function(v) {
        //return /^(128|192|224|24[08]|25[245].0.0.0)|(255.(0|128|192|224|24[08]|25[245]).0.0)|(255.255.(0|128|192|224|24[08]|25[245]).0)|(255.255.255.(0|128|192|224|24[08]|252))$/.test(v);
        // return /(^(128|192|224|24[08]|25[245])\.0\.0\.0$)|(^255\.(0|128|192|224|24[08]|25[245])\.0\.0$)|(^255\.255\.(0|128|192|224|24[08]|25[245])\.0$)|(^255\.255\.255\.(0|128|192|224|24[08]|252)$)/.test(v);
        return /^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})([/]([0-9]|[0-2][0-9]|3[0-2]))$/.test(v);
    },
    IPNetmaskText: esapp.Utils.getTranslation('vtypeipnetmask')  // 'Must be like 192.168.0.0/24'
    ,IPNetmaskMask: /[/.0-9]/
});


//Here is a vType that verifies a proper directory location with a required trailing slash:
//Matches Win and Mac OS paths: x:\foo\bar\, \\foo\bar\, /foo/bar/
Ext.form.VTypes["directory"]=function(v){
 return /^(([a-zA-Z]:){0,1}(\\|\/){1})(([-_.a-zA-Z0-9\\\/ ]+)(\\|\/){1})+$/.test(v);
};
Ext.form.VTypes["directoryText"]=esapp.Utils.getTranslation('vtypedirectory');  // "This must be a valid directory location."
Ext.form.VTypes["directoryMask"]=/[-_.a-zA-Z0-9\\\/: ]/;


//Ext.apply(Ext.form.VTypes, {
//    GeoJSON:  function(v) {
//		v = v.replace(/^\s|\s$/g, ""); //trims string
//		if (v.match(/([^\/\\]+)\.(geojson)$/i) )
//			return true;
//		else
//			return false;
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