Ext.define('esapp.model.MapSet', {
    extend : 'esapp.model.Base',

    fields: [
        {name: 'mapsetcode'},
        {name: 'defined_by'},
        {name: 'descriptive_name'},
        {name: 'description'},
        {name: 'srs_wkt'},
        {name: 'upper_left_long'},
        {name: 'pixel_shift_long'},
        {name: 'rotation_factor_long'},
        {name: 'upper_left_lat'},
        {name: 'pixel_shift_lat'},
        {name: 'rotation_factor_lat'},
        {name: 'pixel_size_x'},
        {name: 'pixel_size_y'},
        {name: 'footprint_image'}
    ],

    autoLoad: true

    ,proxy: {
        type: 'ajax',
        url: 'getmapsetsall',
        reader: {
            type: 'json'
            , successProperty: 'success'
            , rootProperty: 'mapsets'
            , messageProperty: 'message'
        },
        listeners: {
            exception: function (proxy, response, operation) {
                // ToDo: Translate message title or remove message, log error server side and reload proxy (could create and infinite loop?)!
                console.info('MAPSET MODEL- REMOTE EXCEPTION');
            }
        }
    }
});