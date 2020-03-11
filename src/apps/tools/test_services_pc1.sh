#!/bin/bash
rm -f /root/.ssh/known_hosts 1>/dev/null 2>&1
server=$1
Running=0

function check_a_service()
{
  output_dir='/tmp/'
  service_to_check=$1
  server='mesa-pc1'
  tmp_file_log="${output_dir}Status_tellicastd.log"
  expect -c "set timeout -1" -c "spawn ssh -oStrictHostKeyChecking=no  root@${server} \"${service_to_check}\"" \
         -c "expect {*[p-P]assword:} {send \"rootroot\r\"; exp_continue} eof" \
         1>"${tmp_file_log}" 2>&1
  if [ -s ${tmp_file_log} ]
  then
    Permission_Denied_P=$(grep -i "Permission denied" ${tmp_file_log})
    No_Route_To_Host_P=$(grep -i "No route to host" ${tmp_file_log})
    Could_Not_Resolve_P=$(grep -i "Could not resolve hostname" ${tmp_file_log})
    No_Tty_Present_P=$(grep -i "no tty present" ${tmp_file_log})
    No_Askpass_Program_P=$(grep -i "no askpass program specified" ${tmp_file_log})
    Error_P=$(grep -i "error" ${tmp_file_log})
    # Generic error
    if [ -z "${Error_P}" ]
      then
        Error_P=$(grep -i "erreur" ${tmp_file_log})
      fi
        No_Such_File_P=$(grep -i "No such file" ${tmp_file_log})
        if [ -z "${No_Such_File_P}" ]
        then
            No_Such_File_P=$(grep -i "Aucun fichier " ${tmp_file_log})
        fi
    fi
    # List of errors
    if [ -n "${Network_Is_Unreachable_P}" ] || [ -n "${Permission_Denied_P}" ] || \
       [ -n "${No_Route_To_Host_P}" ] || [ -n "${Could_Not_Resolve_P}" ] || \
       [ -n "${No_Tty_Present_P}" ] || [ -n "${No_Askpass_Program_P}" ] || \
       [ -n "${Error_P}" ] || [ -n "${No_Such_File_P}" ]
    then
        if [ -n "${Network_Is_Unreachable_P}" ]
        then
            echo -e "\nNetwork is unreachable !\r" 
        fi
        if [ -n "${Permission_Denied_P}" ]
        then
          echo -e "\nThe root's password is not correct for ${server} !\r" 
        fi
        if [ -n "${No_Route_To_Host_P}" ]
        then
          echo -e "\nNo route to Host for ${server} !\r" 
        fi
        if [ -n "${Could_Not_Resolve_P}" ]
        then
          echo -e "\nThe remote PC ${server} is unknown!\n\rSee the file /etc/hosts.\r"
        fi
        if [ -n "${No_Tty_Present_P}" ] || [ -n "${No_Askpass_Program_P}" ]
        then
          echo -e "\nThe PC ${server} is not correctly configured.\n\rVerify the file /etc/sudoers. Is 'root' declared in this file ?\r"
        fi
        if [ -n "${Error_P}" ]
        then
          nb_lines=$(wc -l ${tmp_file_log} | awk '{ print $1 }')
          if [ ${nb_lines} -gt 2 ]
          then
    		Error_Message=$(tail -n $((${nb_lines} - 2)) ${tmp_file_log} | grep -vi "Password")
    		echo -e "\n${Error_Message}\n\r"
          else
    		echo -e "\nError on the execution ou the command: \"${cmd}\"\n\r\ton the remote PC ${server}.\r"
          fi
        fi
        if [ -n "${No_Such_File_P}" ]
        then
          nb_lines=$(wc -l ${tmp_file_log} | awk '{ print $1 }')
          if [ ${nb_lines} -gt 2 ]
          then
	    Error_Message=$(tail -n $((${nb_lines} - 2)) ${tmp_file_log} | grep -vi "Password")
	    echo -e "\n${Error_Message}\n\r"
          else
	    echo -e "\n\tError on the execution ou the command: \"${cmd}\" . No such file or directory\n\r\ton the remote PC ${server}.\r"
          fi
        fi
        cr=4
    # List of errors - else
    else
        if [ -f ${tmp_file_log} ]
        then
          nb_lines=$(wc -l ${tmp_file_log} | awk '{ print $1 }')
          if [ ${nb_lines} -gt 2 ]
          then
	    # Token=$(tail -n $((${nb_lines} - 2)) ${tmp_file_log} | grep -vi "Password" | grep "Processes" | awk '{ print $2 }')
	    # echo $(tail -n $((${nb_lines} - 2)) ${tmp_file_log})
	    Token=$(tail -n $((${nb_lines} - 2)) ${tmp_file_log} | grep "not running"| awk '{ print $2 }')
	    cat ${tmp_file_log} >> /tmp/mylog

	    # if [[ "$Token" == 'running' ]]; then
	    if [[ $Token == '' ]]; then
	       Running=1
	    else
	       Running=-1
	    fi
	    echo ${Running}
          else
	    echo -e "\r"
          fi
        fi
       cr=0
    rm -f ${tmp_file_log}
  fi

  return ${cr}
}



dvb=$(check_a_service '/etc/init.d/tas_dvbd status')
tellicast=$(check_a_service '/etc/init.d/tas_tellicastd status')
fts=$(check_a_service '/etc/init.d/tas_ftsd status')

echo "dvb=$dvb" "tellicast=$tellicast" "fts=$fts"
