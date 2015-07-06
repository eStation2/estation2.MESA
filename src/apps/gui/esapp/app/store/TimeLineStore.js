Ext.define('esapp.store.TimeLineStore', {
    extend  : 'Ext.data.Store',
    alias: 'store.timeline',

    requires : [
        'esapp.model.TimeLine'
    ],

    model: 'esapp.model.TimeLine',

    storeId : 'TimeLineStore'

//    session: true,
    ,autoLoad: false
    //,remoteSort: false

//    sorters: {property: 'productcode', direction: 'ASC'}

    ,proxy: {
        type : 'jsonp',
        url : 'analysis/gettimeline',
        reader: {
             type: 'array'
            ,successProperty: 'success'
            ,rootProperty: 'timeline'
            ,messageProperty: 'message'
        },
        listeners: {
            exception: function(proxy, response, operation){
                Ext.MessageBox.show({
                    title: 'TIME LINE STORE- REMOTE EXCEPTION',
                    msg: operation.getError(),
                    icon: Ext.MessageBox.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        }
    }
});




//var data = {"success":true, "total":174,"timeline":[
//    {
//        "date": "1998-04-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-04-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-04-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-05-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-05-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-05-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-06-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-06-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-06-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-07-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-07-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-07-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-08-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-08-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-08-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-09-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-09-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-09-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-10-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-10-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-10-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-11-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-11-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-11-21",
//        "present": "true"
//    },
//    {
//        "date": "1998-12-01",
//        "present": "true"
//    },
//    {
//        "date": "1998-12-11",
//        "present": "true"
//    },
//    {
//        "date": "1998-12-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-01-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-01-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-01-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-02-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-02-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-02-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-03-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-03-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-03-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-04-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-04-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-04-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-05-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-05-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-05-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-06-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-06-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-06-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-07-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-07-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-07-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-08-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-08-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-08-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-09-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-09-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-09-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-10-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-10-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-10-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-11-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-11-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-11-21",
//        "present": "true"
//    },
//    {
//        "date": "1999-12-01",
//        "present": "true"
//    },
//    {
//        "date": "1999-12-11",
//        "present": "true"
//    },
//    {
//        "date": "1999-12-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-01-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-01-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-01-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-02-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-02-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-02-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-03-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-03-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-03-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-04-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-04-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-04-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-05-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-05-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-05-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-06-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-06-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-06-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-07-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-07-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-07-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-08-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-08-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-08-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-09-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-09-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-09-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-10-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-10-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-10-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-11-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-11-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-11-21",
//        "present": "true"
//    },
//    {
//        "date": "2000-12-01",
//        "present": "true"
//    },
//    {
//        "date": "2000-12-11",
//        "present": "true"
//    },
//    {
//        "date": "2000-12-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-01-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-01-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-01-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-02-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-02-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-02-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-03-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-03-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-03-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-04-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-04-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-04-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-05-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-05-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-05-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-06-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-06-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-06-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-07-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-07-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-07-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-08-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-08-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-08-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-09-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-09-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-09-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-10-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-10-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-10-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-11-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-11-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-11-21",
//        "present": "true"
//    },
//    {
//        "date": "2001-12-01",
//        "present": "true"
//    },
//    {
//        "date": "2001-12-11",
//        "present": "true"
//    },
//    {
//        "date": "2001-12-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-01-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-01-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-01-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-02-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-02-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-02-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-03-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-03-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-03-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-04-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-04-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-04-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-05-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-05-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-05-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-06-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-06-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-06-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-07-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-07-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-07-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-08-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-08-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-08-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-09-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-09-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-09-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-10-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-10-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-10-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-11-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-11-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-11-21",
//        "present": "true"
//    },
//    {
//        "date": "2002-12-01",
//        "present": "true"
//    },
//    {
//        "date": "2002-12-11",
//        "present": "true"
//    },
//    {
//        "date": "2002-12-21",
//        "present": "true"
//    },
//    {
//        "date": "2003-01-01",
//        "present": "true"
//    },
//    {
//        "date": "2003-01-11",
//        "present": "true"
//    },
//    {
//        "date": "2003-01-21",
//        "present": "true"
//    }
//]};

//esapp.store.TimeLineStore.loadData(data);