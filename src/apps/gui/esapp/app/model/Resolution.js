Ext.define('esapp.model.Resolution', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'resolutioncode'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'pixel_shift_long'},
        {name: 'pixel_shift_lat'}
    ]
});
