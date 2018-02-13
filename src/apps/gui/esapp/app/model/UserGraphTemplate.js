Ext.define('esapp.model.UserGraphTemplate', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'userid', mapping: 'userid'},
        {name: 'graph_tpl_name', type: 'string', mapping: 'templatename'},
        {name: 'graphviewposition', mapping: 'graphviewposition'},
        {name: 'graphviewsize', mapping: 'graphviewsize'},
        {name: 'graph_type', mapping: 'graph_type'},
        {name: 'selectedtimeseries', mapping: 'selectedtimeseries'},
        {name: 'yearts', mapping: 'yearts'},
        {name: 'tsfromperiod', mapping: 'tsfromperiod'},
        {name: 'tstoperiod', mapping: 'tstoperiod'},
        {name: 'yearstocompare', mapping: 'yearstocompare'},
        {name: 'tsfromseason', mapping: 'tsfromseason'},
        {name: 'tstoseason', mapping: 'tstoseason'},
        {name: 'wkt_geom', mapping: 'wkt_geom'},
        {name: 'selectedregionname', mapping: 'selectedregionname'},
        {name: 'disclaimerobjposition', mapping: 'disclaimerobjposition'},
        {name: 'disclaimerobjcontent', type: 'string', mapping: 'disclaimerobjcontent'},
        {name: 'logosobjposition', mapping: 'logosobjposition'},
        {name: 'logosobjcontent', mapping: 'logosobjcontent'},
        {name: 'showobjects',  type: 'boolean', mapping: 'showobjects'},
        {name: 'auto_open',  type: 'boolean', mapping: 'auto_open'}
    ]
});
