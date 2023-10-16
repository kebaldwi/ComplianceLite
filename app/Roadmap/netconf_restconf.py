#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: netconf_restconf.py
# author: gzapodea@cisco.com
# use case: Simple Check of XML audit files against configuration
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
####################################################################################

# This netconf and restconf module is written to address netconf and restconf config of devices

#     ------------------------------- IMPORTS -------------------------------


import requests
import ncclient
import xml
import xml.dom.minidom
import json
import lxml.etree as et
import xmltodict

from ncclient import manager

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth  # for Basic Auth

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings

#     ----------------------------- DEFINITIONS -----------------------------

def netconf_get_hostname(ios_xe_host, ios_xe_port, ios_xe_user, ios_xe_pass):
    """
    This function will retrieve the device hostname via NETCONF
    :param ios_xe_host: device IPv4 address
    :param ios_xe_port: NETCONF port
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return IOS XE device hostname
    """
    with manager.connect(host=ios_xe_host, port=ios_xe_port, username=ios_xe_user,
                         password=ios_xe_pass, hostkey_verify=False,
                         device_params={'name': 'default'},
                         allow_agent=False, look_for_keys=False) as m:
        # XML filter to issue with the get operation
        # IOS-XE 16.6.2+        YANG model called "Cisco-IOS-XE-native"

        hostname_filter = '''
                                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                                        <hostname/>
                                    </native>
                                </filter>
                          '''

        result = m.get(hostname_filter)
        xml_doc = xml.dom.minidom.parseString(result.xml)
        int_info = xml_doc.getElementsByTagName('hostname')
        try:
            hostname = int_info[0].firstChild.nodeValue
        except:
            hostname = 'unknown'
        return hostname


def netconf_get_int_oper_data(interface, ios_xe_host, ios_xe_port, ios_xe_user, ios_xe_pass):
    """
    This function will retrieve the operational data for the interface via NETCONF
    :param interface: interface name
    :param ios_xe_host: device IPv4 address
    :param ios_xe_port: NETCONF port
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return interface operational data in XML
    """

    with manager.connect(host=ios_xe_host, port=ios_xe_port, username=ios_xe_user,
                         password=ios_xe_pass, hostkey_verify=False,
                         device_params={'name': 'default'},
                         allow_agent=False, look_for_keys=False) as m:
        # XML filter to issue with the get operation
        # IOS-XE 16.6.2+        YANG model called "ietf-interfaces"

        interface_state_filter = '''
                                            <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                                <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                                                    <interface>
                                                        <name>''' + interface + '''</name>
                                                    </interface>
                                                </interfaces-state>
                                            </filter>
                                        '''

        try:
            result = m.get(interface_state_filter)
            oper_data = xml.dom.minidom.parseString(result.xml)
        except:
            oper_data = 'unknown'
        return oper_data


def netconf_get_int_oper_status(interface, ios_xe_host, ios_xe_port, ios_xe_user, ios_xe_pass):
    """
    This function will retrieve the IPv4 address configured on the interface via NETCONF
    :param interface: interface name
    :param ios_xe_host: device IPv4 address
    :param ios_xe_port: NETCONF port
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return oper_status: the interface operational status - up/down
    """
    with manager.connect(host=ios_xe_host, port=ios_xe_port, username=ios_xe_user,
                         password=ios_xe_pass, hostkey_verify=False,
                         device_params={'name': 'default'},
                         allow_agent=False, look_for_keys=False) as m:
        # XML filter to issue with the get operation
        # IOS-XE 16.6.2+        YANG model called "ietf-interfaces"

        interface_state_filter = '''
                                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                                            <interface>
                                                <name>''' + interface + '''</name>
                                                <oper-status/>
                                            </interface>
                                        </interfaces-state>
                                    </filter>
                                '''

        result = m.get(interface_state_filter)
        xml_doc = xml.dom.minidom.parseString(result.xml)
        int_info = xml_doc.getElementsByTagName('oper-status')
        try:
            oper_status = int_info[0].firstChild.nodeValue
        except:
            oper_status = 'unknown'
        return oper_status


def netconf_save_running_config_to_file(file_and_path, ios_xe_host, ios_xe_port, ios_xe_user, ios_xe_pass):
    """
    This function will save the running configuration of the device {ios_xe_host} to file
    :param file_and_path: the path and the file name. example flash:/folder/file
    :param ios_xe_host: device IPv4 address
    :param ios_xe_port: NETCONF port
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return success/failed
    """
    # define the rpc payload, source and destination file
    # IOS-XE 16.8+        YANG model called "Cisco-IOS-XE-rpc"
    payload = [
        '''
        <copy xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-rpc">
          <_source>running-config</_source>
          <_destination>''' + file_and_path + '''</_destination>
        </copy>
        '''
    ]

    # connect to netconf agent
    with manager.connect(host=ios_xe_host, port=ios_xe_port, username=ios_xe_user,
                         password=ios_xe_pass, hostkey_verify=False,
                         device_params={'name': 'csr'},
                         allow_agent=False, look_for_keys=False) as m:

        # execute netconf operation
        for rpc in payload:
            try:
                response = m.dispatch(et.fromstring(rpc))
                response_str = json.dumps(xmltodict.parse(str(response)))
                if 'bytes copied' in response_str:
                    result = 'Successful'
                else:
                    result = 'Failed'
                data = response.data_ele
            except RPCError as e:
                data = e._raw
                result = 'Failed'

    return data, result


def restconf_get_hostname(ios_xe_host, ios_xe_user, ios_xe_pass):
    """
    This function will retrieve the device hostname via RESTCONF
    :param ios_xe_host: device IPv4 address
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return IOS XE device hostname
    """
    dev_auth = HTTPBasicAuth(ios_xe_user, ios_xe_pass)
    url = 'https://' + ios_xe_host + '/restconf/data/Cisco-IOS-XE-native:native/hostname'
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    response = requests.get(url, headers=header, verify=False, auth=dev_auth)
    hostname_json = response.json()
    hostname = hostname_json['Cisco-IOS-XE-native:hostname']
    return hostname


def restconf_get_int_oper_data(interface, ios_xe_host, ios_xe_user, ios_xe_pass):
    """
    This function will retrieve the operational data for the interface via RESTCONF
    :param interface: interface name
    :param ios_xe_host: device IPv4 address
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return interface operational data in JSON
    """

    # encode the interface URI: GigabitEthernet0/0/2 - http://10.104.50.97/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=0%2F0%2F2
    # ref.: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/166/b_166_programmability_cg/restconf_prog_int.html

    interface_uri = interface.replace('/', '%2F')
    interface_uri = interface_uri.replace('.', '%2E')
    dev_auth = HTTPBasicAuth(ios_xe_user, ios_xe_pass)
    url = 'https://' + ios_xe_host + '/restconf/data/ietf-interfaces:interfaces-state/interface=' + interface_uri
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    response = requests.get(url, headers=header, verify=False, auth=dev_auth)
    interface_info = response.json()
    oper_data = interface_info['ietf-interfaces:interface']
    return oper_data


def restconf_save_running_config(ios_xe_host, ios_xe_user, ios_xe_pass):
    """
    This function will save the device {ios_xe_host} running configuration to startup-config via RESTCONF
    :param ios_xe_host: device IPv4 address
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return save config operation result
    """
    dev_auth = HTTPBasicAuth(ios_xe_user, ios_xe_pass)
    url = 'https://' + ios_xe_host + '/restconf/operations/cisco-ia:save-config'
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    response = requests.post(url, headers=header, verify=False, auth=dev_auth)
    save_info = response.json()
    save_config_result = save_info['cisco-ia:output']['result']
    return save_config_result


def restconf_rollback_to_saved_config(file_and_path, ios_xe_host, ios_xe_user, ios_xe_pass):
    """
    This function will force a rollback of the device {ios_xe_host} saved configuration {file_and_path}
    to running configuration via RESTCONF
    :param file_and_path: the path and the file name. example flash:/folder/file
    :param ios_xe_host: device IPv4 address
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return save config operation result
    """
    dev_auth = HTTPBasicAuth(ios_xe_user, ios_xe_pass)
    url = 'https://' + ios_xe_host + '/restconf/operations/cisco-ia:rollback'
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    payload = {"rollback": [{"target-url": file_and_path}]}
    response = requests.post(url, headers=header, data=json.dumps(payload), verify=False, auth=dev_auth)
    rollback_info = response.json()
    rollback_result = rollback_info['cisco-ia:output']['result']
    return rollback_result


def restconf_create_checkpoint_config(ios_xe_host, ios_xe_user, ios_xe_pass):
    """
    This function will create a checkpoint config for the device {ios_xe_host} via RESTCONF
    :param ios_xe_host: device IPv4 address
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :param file_and_path: the path and the file name. example flash:/folder/file
    :return save config operation result
    """
    dev_auth = HTTPBasicAuth(ios_xe_user, ios_xe_pass)
    url = 'https://' + ios_xe_host + '/restconf/operations/cisco-ia:checkpoint/'
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    # payload = {"rollback": [{"target-url": file_and_path}]}
    response = requests.post(url, headers=header, verify=False, auth=dev_auth)
    checkpoint_info = response.json()
    print(checkpoint_info)
    checkpoint_result = checkpoint_info['cisco-ia:output']['result']
    return checkpoint_result


def restconf_get_capabilities(ios_xe_host, ios_xe_user, ios_xe_pass):
    """
    This function will retrieve the device capabilities via RESTCONF
    :param ios_xe_host: device IPv4 address
    :param ios_xe_user: username
    :param ios_xe_pass: password
    :return: device capabilities
    """
    dev_auth = HTTPBasicAuth(ios_xe_user, ios_xe_pass)
    url = 'https://' + ios_xe_host + '/restconf/data/netconf-state/capabilities'
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    response = requests.get(url, headers=header, verify=False, auth=dev_auth)
    capabilities_json =  response.json()
    return capabilities_json['ietf-netconf-monitoring:capabilities']

