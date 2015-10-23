<?php

    if ( !session_id() || session_id() == "" ) { /* session not started - was in "and" && */
        session_start();   // Always start the session to have the session variables available!
        if (isset($_SESSION['globals']['session_id'])) {
            session_id(strip_tags($_SESSION['globals']['session_id']));    // get SESSION ID
        }
        else if (isset($_COOKIE["PHPSESSID"])) {
            session_id(strip_tags($_COOKIE['PHPSESSID']));    // get SESSION ID
        }
        else if (isset($_REQUEST["sessionid"])) {
            session_id(strip_tags($_REQUEST['sessionid']));    // get SESSION ID
        }
    }
    $sessionid = session_id();


    if (!isset($_SESSION['db'])  || !is_object($_SESSION['db'])){
        // Include the PostgreSQL class and connect to the database
        // create an instance of the PostgreSQL class in $_SESSION['db'] ).
        require  'PostgreSQL.php';
        // Connect to PostgreSQL
        $_SESSION['db'] = new PostgreSQL();
        if ($_SESSION['db']->isError()) {
            echo $_SESSION['db']->errorMsg();
            exit;
        }
    }


    function prepareForDatabase($text){
        $text = str_replace('"', "'", $text);
        $text = str_replace("'", "''", $text);
        return $text;
    }

    $jsTophp = file_get_contents('dynlist_app_data_edapnav.js');
    $jsTophp = "<?php \n" . $jsTophp;
    $jsTophp = str_replace('CONFIG','$CONFIG' ,$jsTophp);
    $jsTophp = str_replace('new ','' ,$jsTophp);
    $jsTophp = str_replace('data[++inc] ','$data[++$inc]' ,$jsTophp);
    $jsTophp = str_replace('data[inc]','$data[$inc]' ,$jsTophp);

    $file = 'ProductsDataEumetcast.php';
    file_put_contents($file, $jsTophp);

//    echo $jsTophp;

    $CONFIG =  Array();
    $inc  = -1;
    $data =  Array();

    require_once 'ProductsDataEumetcast.php';

    $length = count($data);
    for ($i = 0; $i < $length; $i++) {

			if ($data[$i]['citation_date_creation'].trim()=="")
				$date_creation = "NULL";
			else
				$date_creation = "to_date('".$data[$i]['citation_date_creation']."', 'YYYY-MM-DD')";
				
			if ($data[$i]['citation_date_revision'].trim()=="")
				$date_revision = "NULL";
			else
				$date_revision = "to_date('".$data[$i]['citation_date_revision']."', 'YYYY-MM-DD')";

			if ($data[$i]['citation_date_publication'].trim()=="")
				$date_publication = "NULL";
			else
				$date_publication = "to_date('".$data[$i]['citation_date_publication']."', 'YYYY-MM-DD')";

			if ($data[$i]['dateStamp'].trim()=="")
				$entry_date = "NULL";
			else
				$entry_date = "to_date('".$data[$i]['dateStamp']."', 'YYYY-MM-DD')";

        $online_resources = "";
        for ($resourcenumber = 1; $resourcenumber < 16; $resourcenumber++) {
            $resourcename_nr = 'resources_'.$resourcenumber;
            if (isset($data[$i][$resourcename_nr])){
                $resource = '<a href="'.$data[$i][$resourcename_nr][1].'">'.$data[$i][$resourcename_nr][0].'</a>';
                $online_resources = $online_resources . $resource . "</BR>";
            }
        }

        $data_access = "";
        for ($linknumber = 1; $linknumber < 16; $linknumber++) {
            $linkname_nr = 'link_'.$linknumber;
            if (isset($data[$i][$linkname_nr])){
                $link = '<a href="'.$data[$i][$linkname_nr][1].'">'.$data[$i][$linkname_nr][0].'</a>';
                $data_access = $data_access . $link . "</BR>";
            }
        }


        $qcheckEumetcastRec =   " SELECT * "
                              . " FROM ".DBSCHEMA.".eumetcast_source "
                              . " WHERE eumetcast_id = '".$data[$i]['internalId']."';";

        $result = $_SESSION['db']->query($qcheckEumetcastRec);
        $records = $result->size();

        if($result and ($records == 1)){			

             // Update record.
            $updateRec = "  UPDATE
                              ".DBSCHEMA.".eumetcast_source
                            SET
                              collection_name = '".prepareForDatabase($data[$i]['title'])."',
                              internal_identifier = '".prepareForDatabase($data[$i]['internalId'])."',
                              collection_reference = '".prepareForDatabase($data[$i]['collectionReference'])."',
                              acronym = '".prepareForDatabase($data[$i]['acr'])."',
                              description = '".prepareForDatabase($data[$i]['text'])."',
                              product_status = '".prepareForDatabase($data[$i]['status'])."',
                              date_creation = ".$date_creation.",
                              date_revision = ".$date_revision.",
                              date_publication = ".$date_publication.",
                              west_bound_longitude = ".$data[$i]['boundingBox_west'].",
                              east_bound_longitude = ".$data[$i]['boundingBox_east'].",
                              north_bound_latitude = ".$data[$i]['boundingBox_north'].",
                              south_bound_latitude = ".$data[$i]['boundingBox_south'].",
                              provider_short_name = '".prepareForDatabase($data[$i]['provider'])."',
                              collection_type = '".prepareForDatabase($data[$i]['collectionType'])."',
                              keywords_distribution = '".prepareForDatabase($data[$i]['dissemination'])."',
                              keywords_theme = '".prepareForDatabase($data[$i]['parameter'])."',
                              keywords_societal_benefit_area = '".prepareForDatabase($data[$i]['benefit'])."',
                              orbit_type = '".prepareForDatabase($data[$i]['orbitType'])."',
                              satellite = '".prepareForDatabase($data[$i]['sat'])."',
                              satellite_description = '".prepareForDatabase($data[$i]['satDescription'])."',
                              instrument = '".prepareForDatabase($data[$i]['instrument'])."',
                              spatial_coverage = '".prepareForDatabase($data[$i]['coverage'])."',
                              thumbnails = '".prepareForDatabase($data[$i]['thumbpath'])."',
                              online_resources = '".prepareForDatabase($online_resources)."',
                              distribution = '".prepareForDatabase($data[$i]['dissemination'])."',
                              channels = '".prepareForDatabase($data[$i]['channel'])."',
                              data_access = '".prepareForDatabase($data_access)."',
                              typical_file_name = '".prepareForDatabase($data[$i]['namingconvention'])."',
                              average_file_size = '".prepareForDatabase($data[$i]['filesize'])."',
                              frequency = '".prepareForDatabase($data[$i]['frequency'])."',
                              legal_constraints_access_constraint = '".prepareForDatabase($data[$i]['accessConstraint'])."',
                              legal_use_constraint = '".prepareForDatabase($data[$i]['useConstraint'])."',
                              legal_constraints_data_policy = '".prepareForDatabase($data[$i]['dataPolicy'])."',
                              entry_date = ".$entry_date.",
                              reference_file = '".prepareForDatabase($data[$i]['refFile'])."'
                            WHERE
                              eumetcast_id = '".$data[$i]['internalId']."';";

            echo $updateRec."</BR></BR></BR>";
            $resultUpd = $_SESSION['db']->query($updateRec);
            if ($_SESSION['db']->isError()) {
                echo $_SESSION['db']->errorMsg();
                exit;
            }
            if(!$resultUpd){
                echo "ERROR UPDATE!";
            }
        }
        else {
             // Insert new record.
            $insertRec = "  INSERT INTO products.eumetcast_source
                            (
                              eumetcast_id,
                              filter_expression_jrc,
                              collection_name,
                              status,
                              internal_identifier,
                              collection_reference,
                              acronym,
                              description,
                              product_status,
                              date_creation,
                              date_revision,
                              date_publication,
                              west_bound_longitude,
                              east_bound_longitude,
                              north_bound_latitude,
                              south_bound_latitude,
                              provider_short_name,
                              collection_type,
                              keywords_distribution,
                              keywords_theme,
                              keywords_societal_benefit_area,
                              orbit_type,
                              satellite,
                              satellite_description,
                              instrument,
                              spatial_coverage,
                              thumbnails,
                              online_resources,
                              distribution,
                              channels,
                              data_access,
                              available_format,
                              version,
                              typical_file_name,
                              average_file_size,
                              frequency,
                              legal_constraints_access_constraint,
                              legal_use_constraint,
                              legal_constraints_data_policy,
                              entry_date,
                              reference_file
                            )
                            VALUES ( ".
                                "'".prepareForDatabase($data[$i]['internalId'])."',".
                                "'".prepareForDatabase($data[$i]['namingconvention'])."',".
                                "'".prepareForDatabase($data[$i]['title'])."',".
                                "False,".
                                "'".prepareForDatabase($data[$i]['internalId'])."',".
                                "'".prepareForDatabase($data[$i]['collectionReference'])."',".
                                "'".prepareForDatabase($data[$i]['acr'])."',".
                                "'".prepareForDatabase($data[$i]['text'])."',".
                                "'".prepareForDatabase($data[$i]['status'])."',".
								$date_creation.",".
								$date_revision.",".
								$date_publication.",".
                                $data[$i]['boundingBox_west'].",".
                                $data[$i]['boundingBox_east'].",".
                                $data[$i]['boundingBox_north'].",".
                                $data[$i]['boundingBox_south'].",".
                                "'".prepareForDatabase($data[$i]['provider'])."',".
                                "'".prepareForDatabase($data[$i]['collectionType'])."',".
                                "'".prepareForDatabase($data[$i]['dissemination'])."',".
                                "'".prepareForDatabase($data[$i]['parameter'])."',".
                                "'".prepareForDatabase($data[$i]['benefit'])."',".
                                "'".prepareForDatabase($data[$i]['orbitType'])."',".
                                "'".prepareForDatabase($data[$i]['sat'])."',".
                                "'".prepareForDatabase($data[$i]['satDescription'])."',".
                                "'".prepareForDatabase($data[$i]['instrument'])."',".
                                "'".prepareForDatabase($data[$i]['coverage'])."',".
                                "'".prepareForDatabase($data[$i]['thumbpath'])."',".
                                "'".prepareForDatabase($online_resources)."',".
                                "'".prepareForDatabase($data[$i]['dissemination'])."',".
                                "'".prepareForDatabase($data[$i]['channel'])."',".
                                "'".prepareForDatabase($data_access)."',".
                                "'',".
                                "'',".
                                "'".prepareForDatabase($data[$i]['namingconvention'])."',".
                                "'".prepareForDatabase($data[$i]['filesize'])."',".
                                "'".prepareForDatabase($data[$i]['frequency'])."',".
                                "'".prepareForDatabase($data[$i]['accessConstraint'])."',".
                                "'".prepareForDatabase($data[$i]['useConstraint'])."',".
                                "'".prepareForDatabase($data[$i]['dataPolicy'])."',".
								$entry_date.",".
                                "'".prepareForDatabase($data[$i]['refFile'])."');";

            echo $insertRec."</BR></BR></BR>";
            $resultInsert = $_SESSION['db']->query($insertRec);
            if ($_SESSION['db']->isError()) {
                echo $_SESSION['db']->errorMsg();
                exit;
            }
            if(!$resultInsert){
                echo "ERROR INSERT!";
            }
        }

    }


// *************************************************************************************************************
// Removed fields from table products.eumetcast because these are present in the product navigator GUI
// but are not provided in dynlist_app_data_edapnav.js
//
// EUMETCast.Available Format
// provider_url = '".$data[$i]['resources_2']."',
// provider_originating_centre = '".$data[$i]['title']."',
// product_provider_role = '".$data[$i]['title']."',
// provider_telephone = '".$data[$i]['title']."',
// provider_fax = '".$data[$i]['title']."',
// provider_address = '".$data[$i]['title']."',
// provider_city = '".$data[$i]['title']."',
// provider_administrative_area = '".$data[$i]['title']."',
// provider_country = '".$data[$i]['title']."',
// provider_email = '".$data[$i]['title']."',
// legal_constraints_use_limitation = '".$data[$i]['title']."',
// content_description = '".$data[$i]['title']."',
// available_format = '".$data[$i]['available_format']."',
// version = '".$data[$i]['version']."',
// language = 'English',
// characterset = 'utf8',


// *************************************************************************************************************
// Data fields used from dynlist_app_data_edapnav.js
//
//    $data[$i]['title'] = "Near Real-Time Absorbing Aerosol Index - Metop";
//    $data[$i]['collectionReference'] = "";
//    $data[$i]['internalId'] = "85a12a3e-97bb-48f5-961a-47d977e8852f";
//    $data[$i]['acr'] = "NAR";
//    $data[$i]['text'] = "The AAI indicates the presence of elevated absorbing aerosols in the atmosphere.";
//    $data[$i]['status'] = "";
//    $data[$i]['citation_date_creation'] = "2013-05-02";
//    $data[$i]['citation_date_revision'] = "2010-10-13";
//    $data[$i]['citation_date_publication'] = "2009-04-23";
//    $data[$i]['boundingBox_west'] = "-180.00";
//    $data[$i]['boundingBox_east'] = "180.00";
//    $data[$i]['boundingBox_south'] = "-90.00";
//    $data[$i]['boundingBox_north'] = "90.00";
//    $data[$i]['provider'] = "O3M SAF";
//    $data[$i]['collectionType'] = "dataset";
//    $data[$i]['dissemination'] = "EUMETCast, EUMETCast-Europe";
//    $data[$i]['benefit'] = "Weather, Climate, ";
//    $data[$i]['parameter'] = "Aerosol, Atmosphere, ";
//    $data[$i]['resources_2'] = Array("Ozone_Monitoring_SAF", "http://o3msaf.fmi.fi");
//    $data[$i]['orbitType'] = "LEO";
//    $data[$i]['sat'] = "Metop";
//    $data[$i]['satDescription'] = "Low Earth Orbit Satellite(Metop-A, Metop-B)";
//    $data[$i]['instrument'] = "GOME-2,";
//    $data[$i]['coverage'] = "Full Global";
//    $data[$i]['thumbpath'] = "";
//    $data[$i]['resources_1'] = Array("EUMETSAT Ozone Monitoring SAF page", "http://www.eumetsat.int/website/home/Satellites/GroundSegment/Safs/OzoneandAtmosphericChemistryMonitoring/index.html");
//    $data[$i]['channel'] = "SAF-Europe, ";
//    $data[$i]['link_1'] = Array("EO Portal Registration", "http://eoportal.eumetsat.int/userMgmt");
//    $data[$i]['namingconvention'] = "S-O3M_GOME_NAR_02_M02_20130304172059Z_2013030417359Z_V_D_20130404133801Z.hdf5.gz, S-O3M_GOME_NAR_02_M02_20130416111154Z_2013041611454Z_N_O_20130416120142Z.hdf5.gz, S-O3M_GOME_NAR_02_M01_20130416111154Z_2013041611454Z_N_O_20130416120142Z.hdf5.gz, ";
//    $data[$i]['filesize'] = "220 KB, ";
//    $data[$i]['frequency'] = "";
//    $data[$i]['accessConstraint'] = "copyright";
//    $data[$i]['useConstraint'] = "copyright";
//    $data[$i]['dataPolicy'] = "";
//    $data[$i]['dateStamp'] = "2013-10-11";
//    $data[$i]['refFile'] = "85a12a3e-97bb-48f5-961a-47d977e8852f.html";


// *************************************************************************************************************
// Data fields NOT used from dynlist_app_data_edapnav.js
//
//    $data[$i]['category'] = "";
//    $data[$i]['subcategory'] = "";
//    $data[$i]['formats'] = "";
//    $data[$i]['archiveformats'] = "";
//    $data[$i]['archiveacronym'] = "";
//    $data[$i]['archivefilesizes'] = "";
//    $data[$i]['archivefrequency'] = "";
//    $data[$i]['resolution'] = "";
//    $data[$i]['timeRange_begin'] = "2013-05-02";
//    $data[$i]['timeRange_end'] = "";
//    $data[$i]['descKeyword_place'] = "GEONETCast, SAF Archive & FTP";
//    $data[$i]['descKeyword_discipline'] = "";
//    $data[$i]['instrumentSensor'] = "w1351aaa,";
//    $data[$i]['topicCategory'] = "climatologyMeteorologyAtmosphere";
//    $data[$i]['contentType_code'] = "image";
//    $data[$i]['aggregateId'] = ", ";
//    $data[$i]['coverage_bandDescriptor'] = "Channel 2, ";
//    $data[$i]['coverage_bandSpatialResolution'] = ", ";
//    $data[$i]['coverage_bandUnitDef'] = ", ";