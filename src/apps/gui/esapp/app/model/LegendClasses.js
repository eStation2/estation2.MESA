Ext.define('esapp.model.LegendClasses', {
    extend: 'esapp.model.Base',

    fields: [
        {name: 'legend_id', type:'number'},
        {name: 'from_step', type:'number'},
        {name: 'to_step', type:'number'},
        {name: 'color_rgb', type:'string'},
        {name: 'color_label', type:'string'},
        {name: 'group_label', type:'string'}
    ]
});
