/**
 * Created by tklooju on 3/3/14.
 */
var CONFIG = new Array();
var inc  = -1;
var data = new Array();

require('./dynlist_app_data_edapnav.js');

console.log(data[0]);

var pg = require('pg');
//or native libpq bindings
//var pg = require('pg').native

// postgres://user:password@host:port/database
var conString = "postgres://estation:mesadmin@localhost:5432/estationdb";

var client = new pg.Client(conString);
client.connect(function(err) {
  if(err) {
    return console.error('could not connect to postgres', err);
  }
  client.query('SELECT NOW() AS "theTime"', function(err, result) {
    if(err) {
      return console.error('error running query', err);
    }
    console.log(result.rows[0].theTime);
    //output: Tue Jan 15 2013 19:12:47 GMT-600 (CST)
    client.end();
  });
});