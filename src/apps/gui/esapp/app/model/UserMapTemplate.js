Ext.define('esapp.model.UserMapTemplate', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'templatename', type: 'string', mapping: 'templatename'},
        {name: 'userid', mapping: 'userid'},
        {name: 'mapviewposition', mapping: 'mapviewposition'},
        {name: 'mapviewsize', mapping: 'mapviewsize'},
        {name: 'productcode', mapping: 'productcode'},
        {name: 'subproductcode', mapping: 'subproductcode'},
        {name: 'productversion', mapping: 'productversion'},
        {name: 'mapsetcode', mapping: 'mapsetcode'},
        {name: 'legendid', mapping: 'legendid'},
        {name: 'legendlayout', mapping: 'legendlayout'},
        {name: 'legendobjposition', mapping: 'legendobjposition'},
        {name: 'showlegend',  type: 'boolean', mapping: 'showlegend'},
        {name: 'titleobjposition', mapping: 'titleobjposition'},
        {name: 'titleobjcontent', mapping: 'titleobjcontent'},
        {name: 'disclaimerobjposition', mapping: 'disclaimerobjposition'},
        {name: 'disclaimerobjcontent', type: 'string', mapping: 'disclaimerobjcontent'},
        {name: 'logosobjposition', mapping: 'logosobjposition'},
        {name: 'logosobjcontent', mapping: 'logosobjcontent'},
        {name: 'showobjects',  type: 'boolean', mapping: 'showobjects'},
        {name: 'scalelineobjposition', mapping: 'scalelineobjposition'},
        {name: 'vectorlayers', mapping: 'vectorlayers'},
        {name: 'outmask',  type: 'boolean', mapping: 'outmask'},
        {name: 'outmaskfeature', mapping: 'outmaskfeature'},
        {name: 'auto_open', type: 'boolean', mapping: 'auto_open'},
        {name: 'zoomextent', mapping: 'zoomextent'},
        {name: 'mapsize', mapping: 'mapsize'},
        {name: 'mapcenter', mapping: 'mapcenter'}
    ]
});
