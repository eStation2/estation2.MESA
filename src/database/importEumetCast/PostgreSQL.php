<?php
	/**
	* PostgreSQL.php
	*
	* PostgreSQL Abstraction Layer and Database Connection Class
	* @access public
	* @package EMMA
	*
	* Written by: Jurriaan van 't Klooster
	* Date: January 20, 2009
	* Last Updated:
	*
	* Description:
	*  	Abstracts both the php function calls and the server information to POSTGRESQL
	*  	databases.  Utilizes class variables to maintain connection information such
	*  	as number of rows, result id of last operation, etc.
	*
	* Sample Usage:
	*  include("PostgreSQL.php");
	*  $db = new PostgreSQL();
	*  $db->connect("foobar");
	*  $db->exec("SELECT * from TABLE");
	*  while ($db->nextRow())
	*  {   $rs = $db->fobject();
	*      echo "$rs->description : $rs->color : $rs->price <br>\n";
	*  }
	*
	*/

	/**
	* Environment to connect to
	* @access global constant
	* @var string
	*/


//    require_once '../common/startSession.php';

	require_once 'constants.php';

	class PostgreSQL {

		/**
		* Environment indicator, defined as a global constant "ENVIRONMENT"
		* @access private
		* @var string
		*/
		var $DataBaseReference = ENVIRONMENT;

		/**
		* PostgreSQL server hostname
		* set when connect() is called, defined in set_db_info()
		* @access private
		* @var string
		*/
		var $host;

		/**
		* PostgreSQL port
		* set when connect() is called, defined in set_db_info()
		* @access private
		* @var string
		*/
		var $port;

		/**
		* PostgreSQL username
		* set when connect() is called, defined in set_db_info()
		* @access private
		* @var string
		*/
		var $dbUser;

		/**
		* PostgreSQL user's password
		* set when connect() is called, defined in set_db_info()
		* @access private
		* @var string
		*/
		var $dbPass;

		/**
		* Name of database to use
		* set when connect() is called, defined in set_db_info()
		* @access private
		* @var string
		*/
		var $dbName;

		/**
		* PostgreSQL Resource link identifier stored here
		* set when connect() is called, defined in set_db_info()
		* @access private
		* @var integer
		*/
		var $connectionID = -1;

		/**
		* Stores error messages for connection errors
		* @access private
		* @var string
		*/
		var $connectError;

		/**
		* Stores a row counter, needed to loop through records in postgres.
		* @access private
		* @var integer
		*/
    	var $row = -1;

		/**
		* Stores a pointer to result set.
		* @access private
		* @var integer
		*/
	    var $result = null;

		/**
		* Stores internal error code.
		* @access private
		* @var integer
		*/
	    var $errorCode = 0;


		/**
		* PostgreSQL constructor
		* @param string DataBase reference of the appropriate parameters for database connection, set when connect() is called, defined in set_db_info()
		* @access public
		*/
		function PostgreSQL()
		{
			$this->connect($this->DataBaseReference);
		}

	    //
		/**
		* Set appropriate parameters for database connection  - get these settings from a xml file!
		* @return void
		* @access private
		*/
	    function set_db_info($DataBaseReference){
	        switch ($DataBaseReference){
	            case DEVELOPMENT:
	                $this->host = DEVELOPMENT_HOST;
	                $this->port = DEVELOPMENT_PORT;
	                $this->dbUser = DEVELOPMENT_DBUSER;
	                $this->dbPass = DEVELOPMENT_DBPASS;
	                $this->dbName = DEVELOPMENT_DBNAME;
	                break;
	            case TEST:
                    $this->host = TEST_HOST;
                    $this->port = TEST_PORT;
                    $this->dbUser = TEST_DBUSER;
                    $this->dbPass = TEST_DBPASS;
                    $this->dbName = TEST_DBNAME;
	                break;
	            case PRODUCTION:
                    $this->host = PRODUCTION_HOST;
                    $this->port = PRODUCTION_PORT;
                    $this->dbUser = PRODUCTION_DBUSER;
                    $this->dbPass = PRODUCTION_DBPASS;
                    $this->dbName = PRODUCTION_DBNAME;
	                break;
	            default:
	                // FATAL ERROR - DB REFERENCE UNDEFINED
	        }
	    }

		/**
		* Establishes connection to PostgreSQL and selects a database
		* @return void
		* @access private
		*/
	    function connect($DataBaseReference){
			if (isset($DataBaseReference)) {
	            $this->set_db_info($DataBaseReference);

	            // build connection string based on internal settings.
	            $connStr = '';
	            ($this->host != '')      ? ($connStr .= "host=" . $this->host . " ")            : ($connStr = $connStr);
	            ($this->port != '')      ? ($connStr .= "port=" . $this->port . " ")                : ($connStr = $connStr);
	            ($this->dbName != '')    ? ($connStr .= "dbname=" . $this->dbName . " ")      : ($connStr = $connStr);
	            ($this->dbUser != '')    ? ($connStr .= "user=" . $this->dbUser . " ")            : ($connStr = $connStr);
	            ($this->dbPass != '')    ? ($connStr .= "password=" . $this->dbPass . " ")        : ($connStr = $connStr);
	            $connStr = trim($connStr);
//                echo $connStr;
	            $connID = @pg_connect($connStr);
	            if ($connID != "") {
	                $this->connectionID = $connID;
	                $this->exec("set datestyle='ISO'");
	                return $this->connectionID ;
	            } else {
	                // FATAL ERROR - CONNECTI0N ERROR
	                $this->errorCode = -1;
	                $this->connectionID = -1;
	                return 0;
	            }
	        } else {
	            // FATAL ERROR - FUNCTION CALLED WITH NO PARAMETERS
	            $this->connectionID = -1;
	            return 0;
	        }
	    }

		/**
		* Checks for PostgreSQL errors
		* @return boolean
		* @access public
		*/
		function isError()
		{
			if ($this->errorCode != 0) {
				return true;
			}
			$error = pg_last_error($this->connectionID);
			if (empty($error)) {
				return false;
			} else {
				return true;
			}
		}

		/**
		* Standard method to close connection
		* @return integer
		* @access public
		*/
	    function close() {
	        if ($this->connectionID != "-1") {
	            $this->RollbackTrans(); // rollback transaction before closing
	            $closed = pg_close($this->connectionID);
	            return $closed;
	        } else {
	            // connection does not exist
	            return null;
	        }
	    }

	    // function to execute sql queries
	    function exec($query){
	        if ($this->connectionID != "-1") {
	            $this->result = @pg_exec($this->connectionID, $query);
	        if ($this->numRows() > 0) $this->moveFirst();
	            return $this->result;
	        }
	        else return 0;
	    }

	    // get last error message for db connection
	    function errorMsg() {
	        if ($this->connectionID == "-1") {
	            switch ($this->errorCode) {
	                case -1:
	                    return "FATAL ERROR - DATABASE CONNECTION ERROR: RESOURCE NOT FOUND";
	                    break;
	                case -2:
	                    return "FATAL ERROR - CLASS ERROR: FUNCTION CALLED WITHOUT PARAMETERS";
	                    break;
	                default:
	                    return null;
	            }
	        } else {
	            return pg_errormessage($this->connectionID);
	        }
	    }

	    ////////////////////
	    // Cursor movement
	    ////////////////////

	    // move pointer to first row of result set
	    function moveFirst() {
	        if ($this->result == null) return false;
	        else {
	                $this->setRow(0);
	                return true;
	        }
	    }

	    // move pointer to last row of result set
	    function moveLast() {
	        if ($this->result == null) return false;
	        else {
	                $this->setRow($this->numRows()-1);
	                return true;
	        }
	    }

	    // point to the next row, return false if no next row
	    function moveNext() {
	        // If more rows, then advance row pointer
	        if ($this->row < $this->numRows()-1) {
	            $this->setRow($this->row +1);
	            return true;
	        }
	        else return false;
	    }

	    // point to the previous row, return false if no previous row
	    function movePrevious() {
	        // If not first row, then advance row pointer
	        if ($this->row > 0) {
	            $this->setRow($this->row -1);
	            return true;
	        }
	        else return false;
	    }

	    // point to the next row, return false if no next row
	    function nextRow() {
	        // If more rows, then advance row pointer
	        if ($this->numRows() == '0')
	                return false;
	        elseif ($this->row <= $this->numRows()-1) {
	                $this->setRow($this->row +1);
	                return true;
	        }
	        else return false;
	    }

	    // can be used to set a pointer to a perticular row
	    function setRow($row){
	        $this->row = $row;
	    }

	    ///////////////////////
	    // Result set related
	    ///////////////////////

	    // used to pull the results back
	    function fobject() {
	        if ($this->result == null || $this->row == "-1") return null;
	        else {
	                $object = pg_fetch_object($this->result,$this->row - 1);
	                return $object;
	        }
	    }

	    // another method to obtain results
	    function farray(){
	        if ($this->result == null || $this->row == "-1") return null;
	       else {
	                $arr = pg_fetch_array($this->result,$this->row - 1);
	                return $arr;
	        }
	    }

	    // return number of affected rows by a DELETE, UPDATE, INSERT
	    function numAffected() {
	        if ($this->result == null) return 0; // no result to return result from!
	        else return pg_cmdtuples ($this->result);
	    }

	    // get the number of rows in a result
	    function numRows(){
	        if ($this->result == null) return 0;
	        else {
	                $this->numrows = pg_numrows($this->result);
	                return $this->numrows;
	        }
	    }

	    // return current row
	    function currRow(){
	        return $this->row;
	    }

	    function recordCount() {
	        return $this->numRows();
	    }

	    // get the number of fields in a result
	    function numFields() {
	        if ($this->result == null) return 0;
	        else return pg_numfields ($this->result);
	    }

	    function columnCount() {
	        return $this->numFields();
	    }

	    // get last OID (object identifier) of last INSERT statement
	    function lastOID() {
	        if ($this->result == null) return null;
	        else return pg_getlastoid ($this->result);
	    }

	    // get result field name
	    function fieldname($fieldnum) {
	        if ($this->result == null) return null;
	        else return pg_FieldName($this->result, $fieldnum);
	    }

	    // get result field printed length
	    function fieldLength($fieldname) {
	        if ($this->result == null) return null;
	        else return pg_field_prtlen($this->result, $fieldname);
	    }

	    // get result field storage length
	    function fieldSize($fieldnum) {
	        if ($this->result == null) return null;
	        else return pg_field_size($this->result, $fieldnum);
	    }

	    ////////////////////////
	    // Transaction related
	    ////////////////////////

	    function beginTrans() {
	        return @pg_exec($this->connectionID, "begin");
	    }

	    function commitTrans() {
	        return @pg_exec($this->connectionID, "commit");
	    }

	    // returns true/false
	    function rollbackTrans() {
	        return @pg_exec($this->connectionID, "rollback");
	    }

	    ////////////////////////
	    // SQL String Related
	    ////////////////////////
	    function querySafe($string) {
	        // replace \' with '
	        $string = str_replace("\'", "'", $string);

	        // replace line-break characters
	        $string = str_replace("\n", "", $string);
	        $string = str_replace("\r", "", $string);

	        return $string;
	    }

	    function sqlSafe($string) {
	        // replace \' with \'\'
	        // use this function only for text fields that may contain "'"'s
	        $string = str_replace("\'", "\'\'", $string);
	        return $string;
	    }


		/**
		* Returns an instance of PostgreSQLResult to fetch rows with
		* @param string $sql the database query to run
		* @return PostgreSQLResult
		* @access public
		*/
		function query($sql) // &query($sql)
		{
		if (!$queryResource = pg_query($this->connectionID, $sql)) {
			echo 'Query failed: ' . pg_result_error($queryResource) . ' SQL: ' . $sql;
		}
		return new PostgreSQLResult($this, $queryResource);
		}

	} // end class PostgreSQL


	/**
	* PostgreSQLResult Data Fetching Class
	* @access public
	* @package EMMA
	*/
	class PostgreSQLResult {
		/**
		* Instance of PostgreSQL providing database connection
		* @access private
		* @var PostgreSQL
		*/
		var $PostgreSQL;
		/**
		* Query resource
		* @access private
		* @var resource
		*/
		var $query;
		/**
		* PostgreSQLResult constructor
		* @param object PostgreSQL (instance of PostgreSQL class)
		* @param resource query (PostgreSQL query resource)
		* @access public
		*/
		function PostgreSQLResult(&$PostgreSQL, $query)
		{
			$this->PostgreSQL = &$PostgreSQL;
			$this->query = $query;
		}
		/**
		* Fetches a row from the result
		* @return array
		* @access public
		*/
		function fetch()
		{
			if ( $row = pg_fetch_array($this->query) ) {
				return $row;
			}
			else if ( $this->size() > 0 ) {
				pg_result_seek($this->query, 0);
				return false;
			}
			else {
				return false;
			}
		}

        /**
        * Returns the number of rows selected
        * @return int
        * @access public
        */
        function size()
        {
            return pg_num_rows($this->query);
        }

		/**
		* Checks for PostgreSQL errors
		* @return boolean
		* @access public
		*/
		function isError()
		{
			return $this->PostgreSQL->isError();
		}
	}



    function getDBInfo(){

        $host = '';
        $port = '';
        $dbUser = '';
        $dbPass = '';
        $dbName = '';

        switch ($_SESSION['globals']['environment']){
            case $_SESSION['globals']['development']:
                $host =  $_SESSION['globals']['development_host'];
                $port =  $_SESSION['globals']['development_port'];
                $dbUser =  $_SESSION['globals']['development_dbUser'];
                $dbPass =$_SESSION['globals']['development_dbPass'];
                $dbName = $_SESSION['globals']['development_dbName'];
                break;
            case $_SESSION['globals']['test']:
                $host =  $_SESSION['globals']['test_host'];
                $port =  $_SESSION['globals']['test_port'];
                $dbUser =  $_SESSION['globals']['test_dbUser'];
                $dbPass = $_SESSION['globals']['test_dbPass'];
                $dbName = $_SESSION['globals']['test_dbName'];
                break;
            case $_SESSION['globals']['production']:
                $host = $_SESSION['globals']['production_host'];
                $port = $_SESSION['globals']['production_port'];
                $dbUser =  $_SESSION['globals']['production_dbUser'];
                $dbPass = $_SESSION['globals']['production_dbPass'];
                $dbName = $_SESSION['globals']['production_dbName'];
                break;
            default:
                // FATAL ERROR - DB REFERENCE UNDEFINED
        }

        $dbInfo['host']= $host;
        $dbInfo['port']= $port;
        $dbInfo['dbUser']= $dbUser;
        $dbInfo['dbPass']= $dbPass;
        $dbInfo['dbName']= $dbName;
        return $dbInfo;
    }


//    spl_autoload_extensions('.php,.inc');
//    spl_autoload_call('PostgreSQLResult');
//    spl_autoload_call('PostgreSQL');
//    // Connect to PostgreSQL
//    $db = new PostgreSQL();
//    $_SESSION['db'] = $db;
//
//    if ($db->isError()) {
//        echo $db->errorMsg();
//        exit;
//    }
?>