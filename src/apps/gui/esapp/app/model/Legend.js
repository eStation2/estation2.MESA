Ext.define('esapp.model.Legend', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'legendid', type:'number'},
        {name: 'colourscheme', type:'string'},
        {name: 'legendname', type:'string'},
        {name: 'minvalue', type:'number'},
        {name: 'maxvalue', type:'number'},
        {name: 'legend_descriptive_name', type:'string'},
        {name: 'defined_by', type:'string'},
        {name: 'legend_type', type:'string'}
    ]
});
