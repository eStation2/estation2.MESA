<?php
    /**
     * Constants.php
     *
     * This file is intended to group all constants
     */

    $_SESSION['globals']['environment'] =  'development';
    $_SESSION['globals']['development'] =  'development';
    $_SESSION['globals']['test'] =  'test';
    $_SESSION['globals']['production'] =  'production';

    $_SESSION['globals']['development_host'] =  'localhost';
    $_SESSION['globals']['development_port'] =  '5432';
    $_SESSION['globals']['development_dbUser'] =  'estation';
    $_SESSION['globals']['development_dbPass'] =  'mesadmin';
    $_SESSION['globals']['development_dbName'] =  'estationdb';

    $_SESSION['globals']['test_host'] =  'localhost';
    $_SESSION['globals']['test_port'] =  '5432';
    $_SESSION['globals']['test_dbUser'] =  'estation';
    $_SESSION['globals']['test_dbPass'] =  'mesadmin';
    $_SESSION['globals']['test_dbName'] =  'estationdb';

    $_SESSION['globals']['production_host'] = 'localhost';
    $_SESSION['globals']['production_port'] = '5432';
    $_SESSION['globals']['production_dbUser'] = 'estation';
    $_SESSION['globals']['production_dbPass'] = 'mesadmin';
    $_SESSION['globals']['production_dbName'] = 'estationdb';

    $_SESSION['globals']['schema']= 'products';

    if ( !defined('ENVIRONMENT') ) define("ENVIRONMENT", $_SESSION['globals']['environment']);
    if ( !defined('DEVELOPMENT') ) define("DEVELOPMENT", $_SESSION['globals']['development']);
    if ( !defined('TEST') ) define("TEST", $_SESSION['globals']['test']);
    if ( !defined('PRODUCTION') ) define("PRODUCTION", $_SESSION['globals']['production']);

    define("DBSCHEMA", $_SESSION['globals']['schema']);
    
    define("DEVELOPMENT_HOST", $_SESSION['globals']['development_host']);
    define("DEVELOPMENT_PORT", $_SESSION['globals']['development_port']);
    define("DEVELOPMENT_DBUSER", $_SESSION['globals']['development_dbUser']);
    define("DEVELOPMENT_DBPASS", $_SESSION['globals']['development_dbPass']);
    define("DEVELOPMENT_DBNAME", $_SESSION['globals']['development_dbName']);

    define("TEST_HOST", $_SESSION['globals']['test_host']);
    define("TEST_PORT", $_SESSION['globals']['test_port']);
    define("TEST_DBUSER", $_SESSION['globals']['test_dbUser']);
    define("TEST_DBPASS", $_SESSION['globals']['test_dbPass']);
    define("TEST_DBNAME", $_SESSION['globals']['test_dbName']);

    define("PRODUCTION_HOST", $_SESSION['globals']['production_host']);
    define("PRODUCTION_PORT", $_SESSION['globals']['production_port']);
    define("PRODUCTION_DBUSER", $_SESSION['globals']['production_dbUser']);
    define("PRODUCTION_DBPASS", $_SESSION['globals']['production_dbPass']);
    define("PRODUCTION_DBNAME", $_SESSION['globals']['production_dbName']);

//echo ENVIRONMENT."</BR>";
//echo DEVELOPMENT."</BR>";
//echo TEST."</BR>";
//echo PRODUCTION."</BR>";
//echo DBSCHEMA."</BR>";
//echo DEVELOPMENT_HOST."</BR>";
//echo DEVELOPMENT_PORT."</BR>";
//echo DEVELOPMENT_DBUSER."</BR>";
//echo DEVELOPMENT_DBPASS."</BR>";
//echo DEVELOPMENT_DBNAME."</BR>";


?>