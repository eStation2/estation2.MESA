Ext.define('esapp.view.analysis.mapViewModel', {
    extend: 'Ext.app.ViewModel',
    alias: 'viewmodel.analysis-mapview',

    data: {
        titleData: {
            selected_area: '',
            product_name: '',
            product_date: ''
        },
        logoData: [
            { src:'resources/img/logo/MESA_logo.png', width:'65', height:'50' },
            { src:'resources/img/logo/AfricanUnion_logo.jpg', width:'65', height:'50' },
            { src:'resources/img/logo/ACP_logo.jpg', width:'65', height:'50' },
            { src:'resources/img/logo/logo_en.gif', width:'65', height:'50' }
        ]
    },

    stores: {
        layers: {
            source:'LayersStore'
        }
    }

});
