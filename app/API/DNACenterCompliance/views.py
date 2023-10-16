try:
    from flask import Flask
    from flask_restful import Resource, Api
    from apispec import APISpec
    from marshmallow import Schema, fields
    from apispec.ext.marshmallow import MarshmallowPlugin
    from flask_apispec.extension import FlaskApiSpec
    from flask_apispec.views import MethodResource
    from flask_apispec import marshal_with, doc, use_kwargs
    import requests
    import json
    import time
    import urllib3
    import utils
    
    from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
    from requests.auth import HTTPBasicAuth  # for Basic Auth
    from configuration_template import DNAC_URL, DNAC_PASS, DNAC_USER        
    from dnac_apis import *    
    
    print("All imports are ok............")
except Exception as e:
    print("Error: {} ".format(e))

class DNACenterControllerSchema(Schema):
    name = fields.String(required=True, description="name is required ", example="Keith")

class DNACenterCompliance(MethodResource, Resource):
    import difference_engine
    import compliance_mon
    import prime_compliance_dictionary
    import report_module
    import system_setup
    import service_email
    import service_scheduler
    import utils
    import dnac_apis
    @doc(description='DNA Center Compliance Lite API', tags=['DNA Center Compliance'])
    @use_kwargs(DNACenterControllerSchema, location=('json'))
    def post(self, **kwargs):
        _message = kwargs.get("name", "default")
        response = {"message":"Good Day " + _message}
        return response
    
class WeatherControllerSchema(Schema):
    zip = fields.String(required=True, description="zip code",example='66085')
    city = fields.String(required=False, description="city name",example='Overland Park')

class WeatherController(MethodResource, Resource):
    import json
    import requests
    @doc(description='Verification things are working with weather test', tags=['Health and testing Endpoints'])
    @use_kwargs(WeatherControllerSchema, location=('json'))
    def post(self, **kwargs):
        #url = """http://192.241.187.136/data/2.5/weather?zip=10001,us&appid=11a1aac6bc7d01ea13f0d2a8e78c227e"""
        url = """http://192.241.187.136/data/2.5/weather?zip=""" + str(kwargs.get("zip", "10001")) + """,us&appid=11a1aac6bc7d01ea13f0d2a8e78c227e"""
        my_response = requests.get(url)
        our_response_content = my_response.content.decode('utf8')
        proper_json_response = json.loads(our_response_content)
        
        _message = kwargs.get("zip", "10001")
        _message2 = kwargs.get("city", "Overland Park")
        response = {"message":"Weather JSON response for zip code:" + str(_message) + "\n\n" + str(proper_json_response) + "\n\n" + url + _message2}
        return response
 
class DNACTokenControllerSchema(Schema):
    name = fields.String(required=True, description="name is required ", example="Keith")

class DNACTokenController(MethodResource, Resource):
    @doc(description="Get DNAC Token", tags=["DNAC API's"])
    @use_kwargs(DNACTokenControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
    
        url = DNAC_URL + '/dna/system/api/v1/auth/token'
        header = {'content-type': 'application/json'}
        response = requests.post(url, auth=DNAC_AUTH, headers=header, verify=False)
        dnac_jwt_token = response.json()['Token']
        return dnac_jwt_token
    
class get_all_device_infoControllerSchema(Schema):
    dnac_jwt_token = fields.String(required=True, description="Token is required ", example="00000")

class get_all_device_infoController(MethodResource, Resource):
    @doc(description="get_all_device_info", tags=["DNAC API's"])
    @use_kwargs(get_all_device_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
    
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
        url = DNAC_URL + '/api/v1/network-device'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        all_device_response = requests.get(url, headers=header, verify=False)
        all_device_info = all_device_response.json()
        return all_device_info['response']
    
class get_device_infoControllerSchema(Schema):
    device_id = fields.String(required=True, description="device_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_infoController(MethodResource, Resource):
    @doc(description="get_device_info", tags=["DNAC API's"])
    @use_kwargs(get_device_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_id = kwargs.get("device_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/network-device?id=' + device_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        device_response = requests.get(url, headers=header, verify=False)
        device_info = device_response.json()
        return device_info['response'][0]
    
class delete_deviceControllerSchema(Schema):
    device_id = fields.String(required=True, description="device_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class delete_deviceController(MethodResource, Resource):
    @doc(description="delete_device", tags=["DNAC API's"])
    @use_kwargs(delete_deviceControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_id = kwargs.get("device_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/dna/intent/api/v1/network-device/' + device_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.delete(url, headers=header, verify=False)
        delete_response = response.json()
        delete_status = delete_response['response']
        return delete_status    
    
class get_project_idControllerSchema(Schema):
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_project_idController(MethodResource, Resource):
    @doc(description="get_project_id", tags=["DNAC API's"])
    @use_kwargs(get_project_idControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        project_name = kwargs.get("project_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/template-programmer/project?name=' + project_name
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        proj_json = response.json()
        proj_id = proj_json[0]['id']
        return proj_id

class get_project_infoControllerSchema(Schema):
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_project_infoController(MethodResource, Resource):
    @doc(description="get_project_info", tags=["DNAC API's"])
    @use_kwargs(get_project_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        project_name = kwargs.get("project_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/template-programmer/project?name=' + project_name
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        project_json = response.json()
        template_list = project_json[0]['templates']
        return template_list

class create_commit_templateControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    cli_template = fields.String(required=True, description="cli_template is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class create_commit_templateController(MethodResource, Resource):
    @doc(description="create_commit_template", tags=["DNAC API's"])
    @use_kwargs(create_commit_templateControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        cli_template = kwargs.get("cli_template", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        project_id = get_project_id(project_name, dnac_jwt_token)
    
        # prepare the template param to sent to DNA C
        payload = {
                "name": template_name,
                "description": "Remote router configuration",
                "tags": [],
                "author": "admin",
                "deviceTypes": [
                    {
                        "productFamily": "Routers"
                    },
                    {
                        "productFamily": "Switches and Hubs"
                    }
                ],
                "softwareType": "IOS-XE",
                "softwareVariant": "XE",
                "softwareVersion": "",
                "templateContent": cli_template,
                "rollbackTemplateContent": "",
                "templateParams": [],
                "rollbackTemplateParams": [],
                "parentTemplateId": project_id
            }
    
        # check and delete older versions of the template
        # template_id = get_template_id(template_name, project_name, dnac_jwt_token)
        # if template_id:
        #    delete_template(template_name, project_name, dnac_jwt_token)
    
        # create the new template
        url = DNAC_URL + '/api/v1/template-programmer/project/' + project_id + '/template'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    
        # get the template id
        template_id = get_template_id(template_name, project_name, dnac_jwt_token)
    
        # commit template
        commit_template(template_id, 'committed by Python script', dnac_jwt_token)
    
    
    

class commit_templateControllerSchema(Schema):
    template_id = fields.String(required=True, description="template_id is required ", example="00000")
    comments = fields.String(required=True, description="comments is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class commit_templateController(MethodResource, Resource):
    @doc(description="commit_template", tags=["DNAC API's"])
    @use_kwargs(commit_templateControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_id = kwargs.get("template_id", "10001")
        comments = kwargs.get("comments", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/template-programmer/template/version'
        payload = {
                "templateId": template_id,
                "comments": comments
            }
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
        return response

class update_commit_templateControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    cli_template = fields.String(required=True, description="cli_template is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class update_commit_templateController(MethodResource, Resource):
    @doc(description="update_commit_template", tags=["DNAC API's"])
    @use_kwargs(update_commit_templateControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        cli_template = kwargs.get("cli_template", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        # get the project id
        project_id = get_project_id(project_name, dnac_jwt_token)
    
        # get the template id
        template_id = get_template_id(template_name, project_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/template-programmer/template'
    
        # prepare the template param to sent to DNA C
        payload = {
            "name": template_name,
            "description": "Remote router configuration",
            "tags": [],
            "id": template_id,
            "author": "admin",
            "deviceTypes": [
                {
                    "productFamily": "Routers"
                },
                {
                    "productFamily": "Switches and Hubs"
                }
            ],
            "softwareType": "IOS-XE",
            "softwareVariant": "XE",
            "softwareVersion": "",
            "templateContent": cli_template,
            "rollbackTemplateContent": "",
            "templateParams": [],
            "rollbackTemplateParams": [],
            "parentTemplateId": project_id
        }
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.put(url, data=json.dumps(payload), headers=header, verify=False)
    
        # commit template
        commit_template(template_id, 'committed by Python script', dnac_jwt_token)

class upload_templateControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    cli_template = fields.String(required=True, description="cli_template is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class upload_templateController(MethodResource, Resource):
    @doc(description="upload_template", tags=["DNAC API's"])
    @use_kwargs(upload_templateControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        cli_template = kwargs.get("cli_template", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        template_id = get_template_id(template_name, project_name, dnac_jwt_token)
        if template_id:
            update_commit_template(template_name, project_name, cli_template, dnac_jwt_token)
        else:
            create_commit_template(template_name, project_name, cli_template, dnac_jwt_token)

class delete_templateControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class delete_templateController(MethodResource, Resource):
    @doc(description="delete_template", tags=["DNAC API's"])
    @use_kwargs(delete_templateControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        template_id = get_template_id(template_name, project_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/template-programmer/template/' + template_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.delete(url, headers=header, verify=False)

class get_all_template_infoControllerSchema(Schema):
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_all_template_infoController(MethodResource, Resource):
    @doc(description="get_all_template_info", tags=["DNAC API's"])
    @use_kwargs(get_all_template_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/template-programmer/template'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        all_template_list = response.json()
        return all_template_list

class get_template_name_infoControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_template_name_infoController(MethodResource, Resource):
    @doc(description="get_template_name_info", tags=["DNAC API's"])
    @use_kwargs(get_template_name_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        template_id = get_template_id(template_name, project_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/template-programmer/template/' + template_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        template_json = response.json()
        return template_json

class get_template_idControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_template_idController(MethodResource, Resource):
    @doc(description="get_template_id", tags=["DNAC API's"])
    @use_kwargs(get_template_idControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        template_list = get_project_info(project_name, dnac_jwt_token)
        template_id = None
        for template in template_list:
            if template['name'] == template_name:
                template_id = template['id']
        return template_id

class get_template_id_versionControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_template_id_versionController(MethodResource, Resource):
    @doc(description="get_template_id_version", tags=["DNAC API's"])
    @use_kwargs(get_template_id_versionControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        project_id = get_project_id(project_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/template-programmer/template?projectId=' + project_id + '&includeHead=false'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        project_json = response.json()
        for template in project_json:
            if template['name'] == template_name:
                version = 0
                versions_info = template['versionsInfo']
                for ver in versions_info:
                    if int(ver['version']) > version:
                        template_id_ver = ver['id']
                        version = int(ver['version'])
        return template_id_ver

class deploy_templateControllerSchema(Schema):
    template_name = fields.String(required=True, description="template_name is required ", example="00000")
    project_name = fields.String(required=True, description="project_name is required ", example="00000")
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class deploy_templateController(MethodResource, Resource):
    @doc(description="deploy_template", tags=["DNAC API's"])
    @use_kwargs(deploy_templateControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        template_name = kwargs.get("template_name", "10001")
        project_name = kwargs.get("project_name", "10001")
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        device_management_ip = get_device_management_ip(device_name, dnac_jwt_token)
        template_id = get_template_id_version(template_name, project_name, dnac_jwt_token)
        payload = {
                "templateId": template_id,
                "targetInfo": [
                    {
                        "id": device_management_ip,
                        "type": "MANAGED_DEVICE_IP",
                        "params": {}
                    }
                ]
            }
        url = DNAC_URL + '/api/v1/template-programmer/template/deploy'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, headers=header, data=json.dumps(payload), verify=False)
        depl_task_id = (response.json())["deploymentId"]
        return depl_task_id

class check_template_deployment_statusControllerSchema(Schema):
    depl_task_id = fields.String(required=True, description="depl_task_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class check_template_deployment_statusController(MethodResource, Resource):
    @doc(description="check_template_deployment_status", tags=["DNAC API's"])
    @use_kwargs(check_template_deployment_statusControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        depl_task_id = kwargs.get("depl_task_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/template-programmer/template/deploy/status/' + depl_task_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        response_json = response.json()
        deployment_status = response_json["status"]
        return deployment_status

class get_client_infoControllerSchema(Schema):
    client_ip = fields.String(required=True, description="client_ip is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_client_infoController(MethodResource, Resource):
    @doc(description="get_client_info", tags=["DNAC API's"])
    @use_kwargs(get_client_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        client_ip = kwargs.get("client_ip", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/host?hostIp=' + client_ip
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        client_json = response.json()
        try:
            client_info = client_json['response'][0]
            return client_info
        except:
            return None

class locate_client_ipControllerSchema(Schema):
    client_ip = fields.String(required=True, description="client_ip is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class locate_client_ipController(MethodResource, Resource):
    @doc(description="locate_client_ip", tags=["DNAC API's"])
    @use_kwargs(locate_client_ipControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        client_ip = kwargs.get("client_ip", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
    
        client_info = get_client_info(client_ip, dnac_jwt_token)
        if client_info is not None:
            hostname = client_info['connectedNetworkDeviceName']
            interface_name = client_info['connectedInterfaceName']
            vlan_id = client_info['vlanId']
            return hostname, interface_name, vlan_id
        else:
            return None
        
class get_device_id_nameControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_id_nameController(MethodResource, Resource):
    @doc(description="get_device_id_name", tags=["DNAC API's"])
    @use_kwargs(get_device_id_nameControllerSchema, location=('json'))
    def post(self, **kwargs):
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        device_id = None
        device_list = get_all_device_info(dnac_jwt_token)
        for device in device_list:
            if device['hostname'] == device_name:
                device_id = device['id']
        return device_id        

class get_device_statusControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_statusController(MethodResource, Resource):
    @doc(description="get_device_status", tags=["DNAC API's"])
    @use_kwargs(get_device_statusControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
          
        device_id = get_device_id_name(device_name, dnac_jwt_token)
        if device_id is None:
            return 'UNKNOWN'
        else:
            device_info = get_device_info(device_id, dnac_jwt_token)
            if device_info['reachabilityStatus'] == 'Reachable':
                return 'SUCCESS'
            else:
                return 'FAILURE'

class get_device_management_ipControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_management_ipController(MethodResource, Resource):
    @doc(description="get_device_management_ip", tags=["DNAC API's"])
    @use_kwargs(get_device_management_ipControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        device_ip = None
        device_list = get_all_device_info(dnac_jwt_token)
        for device in device_list:
            if device['hostname'] == device_name:
                device_ip = device['managementIpAddress']
        return device_ip
    
    
    

class get_device_id_snControllerSchema(Schema):
    device_sn = fields.String(required=True, description="device_sn is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_id_snController(MethodResource, Resource):
    @doc(description="get_device_id_sn", tags=["DNAC API's"])
    @use_kwargs(get_device_id_snControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_sn = kwargs.get("device_sn", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/network-device/serial-number/' + device_sn
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        device_response = requests.get(url, headers=header, verify=False)
        device_info = device_response.json()
        device_id = device_info['response']['id']
        return device_id

class get_device_locationControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_locationController(MethodResource, Resource):
    @doc(description="get_device_location", tags=["DNAC API's"])
    @use_kwargs(get_device_locationControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        device_id = get_device_id_name(device_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/group/member/' + device_id + '?groupType=SITE'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        device_response = requests.get(url, headers=header, verify=False)
        device_info = (device_response.json())['response']
        device_location = device_info[0]['groupNameHierarchy']
        return device_location

class create_siteControllerSchema(Schema):
    site_name = fields.String(required=True, description="site_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class create_siteController(MethodResource, Resource):
    @doc(description="create_site", tags=["DNAC API's"])
    @use_kwargs(create_siteControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        site_name = kwargs.get("site_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        payload = {
            "additionalInfo": [
                {
                    "nameSpace": "Location",
                    "attributes": {
                        "type": "area"
                    }
                }
            ],
            "groupNameHierarchy": "Global/" + site_name,
            "groupTypeList": [
                "SITE"
            ],
            "systemGroup": False,
            "parentId": "",
            "name": site_name,
            "id": ""
        }
        url = DNAC_URL + '/api/v1/group'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        requests.post(url, data=json.dumps(payload), headers=header, verify=False)
        

class get_site_idControllerSchema(Schema):
    site_name = fields.String(required=True, description="site_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_site_idController(MethodResource, Resource):
    @doc(description="get_site_id", tags=["DNAC API's"])
    @use_kwargs(get_site_idControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        site_name = kwargs.get("site_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        site_id = None
        url = DNAC_URL + '/api/v1/group?groupType=SITE'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        site_response = requests.get(url, headers=header, verify=False)
        site_json = site_response.json()
        site_list = site_json['response']
        for site in site_list:
            if site_name == site['name']:
                site_id = site['id']
        return site_id

class create_buildingControllerSchema(Schema):
    site_name = fields.String(required=True, description="site_name is required ", example="00000")
    building_name = fields.String(required=True, description="building_name is required ", example="00000")
    address = fields.String(required=True, description="address is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class create_buildingController(MethodResource, Resource):
    @doc(description="create_building", tags=["DNAC API's"])
    @use_kwargs(create_buildingControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        site_name = kwargs.get("site_name", "10001")
        building_name = kwargs.get("building_name", "10001")
        address = kwargs.get("address", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        # get the site id for the site name
        site_id = get_site_id(site_name, dnac_jwt_token)
    
        # get the geolocation info for address
        geo_info = get_geo_info(address, GOOGLE_API_KEY)
        #print('Geolocation info for the address ', address, ' is:')
        #pprint(geo_info)
    
        payload = {
            "additionalInfo": [
                {
                    "nameSpace": "Location",
                    "attributes": {
                        "country": "United States",
                        "address": address,
                        "latitude": geo_info['lat'],
                        "type": "building",
                        "longitude": geo_info['lng']
                    }
                }
            ],
            "groupNameHierarchy": "Global/" + site_name + '/' + building_name,
            "groupTypeList": [
                "SITE"
            ],
            "systemGroup": False,
            "parentId": site_id,
            "name": building_name,
            "id": ""
        }
        url = DNAC_URL + '/api/v1/group'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        requests.post(url, data=json.dumps(payload), headers=header, verify=False)
    
class get_building_idControllerSchema(Schema):
    building_name = fields.String(required=True, description="building_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_building_idController(MethodResource, Resource):
    @doc(description="get_building_id", tags=["DNAC API's"])
    @use_kwargs(get_building_idControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        building_name = kwargs.get("building_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        building_id = None
        url = DNAC_URL + '/api/v1/group?groupType=SITE'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        building_response = requests.get(url, headers=header, verify=False)
        building_json = building_response.json()
        building_list = building_json['response']
        for building in building_list:
            if building_name == building['name']:
                building_id = building['id']
        return building_id

class create_floorControllerSchema(Schema):
    building_name = fields.String(required=True, description="building_name is required ", example="00000")
    floor_name = fields.String(required=True, description="floor_name is required ", example="00000")
    floor_number = fields.String(required=True, description="floor_number is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class create_floorController(MethodResource, Resource):
    @doc(description="create_floor", tags=["DNAC API's"])
    @use_kwargs(create_floorControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        building_name = kwargs.get("building_name", "10001")
        floor_name = kwargs.get("floor_name", "10001")
        floor_number = kwargs.get("floor_number", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        # get the site id
        building_id = get_building_id(building_name, dnac_jwt_token)
    
        payload = {
            "additionalInfo": [
                {
                    "nameSpace": "Location",
                    "attributes": {
                        "type": "floor"
                    }
                },
                {
                    "nameSpace": "mapGeometry",
                    "attributes": {
                        "offsetX": "0.0",
                        "offsetY": "0.0",
                        "width": "200.0",
                        "length": "100.0",
                        "geometryType": "DUMMYTYPE",
                        "height": "20.0"
                    }
                },
                {
                    "nameSpace": "mapsSummary",
                    "attributes": {
                        "floorIndex": floor_number
                    }
                }
            ],
            "groupNameHierarchy": "",
            "groupTypeList": [
                "SITE"
            ],
            "name": floor_name,
            "parentId": building_id,
            "systemGroup": False,
            "id": ""
        }
        url = DNAC_URL + '/api/v1/group'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        requests.post(url, data=json.dumps(payload), headers=header, verify=False)

class get_floor_idControllerSchema(Schema):
    building_name = fields.String(required=True, description="building_name is required ", example="00000")
    floor_name = fields.String(required=True, description="floor_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_floor_idController(MethodResource, Resource):
    @doc(description="get_floor_id", tags=["DNAC API's"])
    @use_kwargs(get_floor_idControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        building_name = kwargs.get("building_name", "10001")
        floor_name = kwargs.get("floor_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        floor_id = None
        building_id = get_building_id(building_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/group/' + building_id + '/child?level=1'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        building_response = requests.get(url, headers=header, verify=False)
        building_json = building_response.json()
        floor_list = building_json['response']
        for floor in floor_list:
            if floor['name'] == floor_name:
                floor_id = floor['id']
        return floor_id
    
class assign_device_sn_buildingControllerSchema(Schema):
    device_sn = fields.String(required=True, description="device_sn is required ", example="00000")
    building_name = fields.String(required=True, description="building_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class assign_device_sn_buildingController(MethodResource, Resource):
    @doc(description="assign_device_sn_building", tags=["DNAC API's"])
    @use_kwargs(assign_device_sn_buildingControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_sn = kwargs.get("device_sn", "10001")
        building_name = kwargs.get("building_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        # get the building and device id's
        building_id = get_building_id(building_name, dnac_jwt_token)
        device_id = get_device_id_sn(device_sn, dnac_jwt_token)
    
        url = DNAC_URL + '/api/v1/group/' + building_id + '/member'
        payload = {"networkdevice": [device_id]}
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
        #print('Device with the SN: ', device_sn, 'assigned to building: ', building_name)

class assign_device_name_buildingControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    building_name = fields.String(required=True, description="building_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class assign_device_name_buildingController(MethodResource, Resource):
    @doc(description="assign_device_name_building", tags=["DNAC API's"])
    @use_kwargs(assign_device_name_buildingControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_name = kwargs.get("device_name", "10001")
        building_name = kwargs.get("building_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        # get the building and device id's
        building_id = get_building_id(building_name, dnac_jwt_token)
        device_id = get_device_id_name(device_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/group/' + building_id + '/member'
        payload = {"networkdevice": [device_id]}
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
        #print('Device with the name: ', device_name, 'assigned to building: ', building_name)

class get_geo_infoControllerSchema(Schema):
    address = fields.String(required=True, description="address is required ", example="00000")
    google_key = fields.String(required=True, description="google_key is required ", example="00000")

class get_geo_infoController(MethodResource, Resource):
    @doc(description="get_geo_info", tags=["DNAC API's"])
    @use_kwargs(get_geo_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        address = kwargs.get("address", "10001")
        google_key = kwargs.get("google_key", "10001")
    
        url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + google_key
        header = {'content-type': 'application/json'}
        response = requests.get(url, headers=header, verify=False)
        response_json = response.json()
        location_info = response_json['results'][0]['geometry']['location']
        return location_info

class sync_deviceControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class sync_deviceController(MethodResource, Resource):
    @doc(description="sync_device", tags=["DNAC API's"])
    @use_kwargs(sync_deviceControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        device_id = get_device_id_name(device_name, dnac_jwt_token)
        param = [device_id]
        url = DNAC_URL + '/api/v1/network-device/sync?forceSync=true'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        sync_response = requests.put(url, data=json.dumps(param), headers=header, verify=False)
        task = sync_response.json()['response']['taskId']
        return sync_response.status_code, task

class check_task_id_statusControllerSchema(Schema):
    task_id = fields.String(required=True, description="task_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class check_task_id_statusController(MethodResource, Resource):
    @doc(description="check_task_id_status", tags=["DNAC API's"])
    @use_kwargs(check_task_id_statusControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        task_id = kwargs.get("task_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/task/' + task_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        task_response = requests.get(url, headers=header, verify=False)
        task_json = task_response.json()
        task_status = task_json['response']['isError']
        if not task_status:
            task_result = 'SUCCESS'
        else:
            task_result = 'FAILURE'
        return task_result

class check_task_id_outputControllerSchema(Schema):
    task_id = fields.String(required=True, description="task_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class check_task_id_outputController(MethodResource, Resource):
    @doc(description="check_task_id_output", tags=["DNAC API's"])
    @use_kwargs(check_task_id_outputControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        task_id = kwargs.get("task_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/task/' + task_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        completed = 'no'
        while completed == 'no':
            try:
                task_response = requests.get(url, headers=header, verify=False)
                task_json = task_response.json()
                task_output = task_json['response']
                completed = 'yes'
            except:
                time.sleep(1)
        return task_output

class create_path_traceControllerSchema(Schema):
    src_ip = fields.String(required=True, description="src_ip is required ", example="00000")
    dest_ip = fields.String(required=True, description="dest_ip is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class create_path_traceController(MethodResource, Resource):
    @doc(description="create_path_trace", tags=["DNAC API's"])
    @use_kwargs(create_path_traceControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        src_ip = kwargs.get("src_ip", "10001")
        dest_ip = kwargs.get("dest_ip", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
    
        param = {
            'destIP': dest_ip,
            'periodicRefresh': False,
            'sourceIP': src_ip
        }
    
        url = DNAC_URL + '/api/v1/flow-analysis'
        header = {'accept': 'application/json', 'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        path_response = requests.post(url, data=json.dumps(param), headers=header, verify=False)
        path_json = path_response.json()
        path_id = path_json['response']['flowAnalysisId']
        return path_id

class get_path_trace_infoControllerSchema(Schema):
    path_id = fields.String(required=True, description="path_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_path_trace_infoController(MethodResource, Resource):
    @doc(description="get_path_trace_info", tags=["DNAC API's"])
    @use_kwargs(get_path_trace_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        path_id = kwargs.get("path_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
    
        url = DNAC_URL + '/api/v1/flow-analysis/' + path_id
        header = {'accept': 'application/json', 'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        path_response = requests.get(url, headers=header, verify=False)
        path_json = path_response.json()
        path_info = path_json['response']
        path_status = path_info['request']['status']
        path_list = []
        if path_status == 'COMPLETED':
            network_info = path_info['networkElementsInfo']
            path_list.append(path_info['request']['sourceIP'])
            for elem in network_info:
                try:
                    path_list.append(elem['ingressInterface']['physicalInterface']['name'])
                except:
                    pass
                try:
                    path_list.append(elem['name'])
                except:
                    pass
                try:
                    path_list.append(elem['egressInterface']['physicalInterface']['name'])
                except:
                    pass
            path_list.append(path_info['request']['destIP'])
        return path_status, path_list

class check_ipv4_network_interfaceControllerSchema(Schema):
    ip_address = fields.String(required=True, description="ip_address is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class check_ipv4_network_interfaceController(MethodResource, Resource):
    @doc(description="check_ipv4_network_interface", tags=["DNAC API's"])
    @use_kwargs(check_ipv4_network_interfaceControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        ip_address = kwargs.get("ip_address", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/interface/ip-address/' + ip_address
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        response_json = response.json()
        try:
            response_info = response_json['response'][0]
            interface_name = response_info['portName']
            device_id = response_info['deviceId']
            #device_info = get_device_info(device_id, dnac_jwt_token)
            url = DNAC_URL + '/api/v1/network-device?id=' + device_id
            header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
            device_response = requests.get(url, headers=header, verify=False)
            device_info = device_response.json()            
            device_hostname = device_info['hostname']
            return device_hostname, interface_name
        except:
            device_info = get_device_info_ip(ip_address, dnac_jwt_token)  # required for AP's
            device_hostname = device_info['hostname']
            return device_hostname, ''

class get_device_info_ipControllerSchema(Schema):
    ip_address = fields.String(required=True, description="ip_address is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_info_ipController(MethodResource, Resource):
    @doc(description="get_device_info_ip", tags=["DNAC API's"])
    @use_kwargs(get_device_info_ipControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        ip_address = kwargs.get("ip_address", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/network-device/ip-address/' + ip_address
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        response_json = response.json()
        device_info = response_json['response']
        if 'errorCode' == 'Not found':
            return None
        else:
            return device_info

class get_legit_cli_command_runnerControllerSchema(Schema):
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_legit_cli_command_runnerController(MethodResource, Resource):
    @doc(description="get_legit_cli_command_runner", tags=["DNAC API's"])
    @use_kwargs(get_legit_cli_command_runnerControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/network-device-poller/cli/legit-reads'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        response_json = response.json()
        cli_list = response_json['response']
        return cli_list

class get_content_file_idControllerSchema(Schema):
    file_id = fields.String(required=True, description="file_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_content_file_idController(MethodResource, Resource):
    @doc(description="get_content_file_id", tags=["DNAC API's"])
    @use_kwargs(get_content_file_idControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        file_id = kwargs.get("file_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/file/' + file_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False, stream=True)
        response_json = response.json()
        return response_json

class get_output_command_runnerControllerSchema(Schema):
    command = fields.String(required=True, description="command is required ", example="00000")
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_output_command_runnerController(MethodResource, Resource):
    @doc(description="get_output_command_runner", tags=["DNAC API's"])
    @use_kwargs(get_output_command_runnerControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        command = kwargs.get("command", "10001")
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
    
        # get the DNA C device id
        device_id = get_device_id_name(device_name, dnac_jwt_token)
    
        # get the DNA C task id that will process the CLI command runner
        payload = {
            "commands": [command],
            "deviceUuids": [device_id],
            "timeout": 0
            }
        url = DNAC_URL + '/api/v1/network-device-poller/cli/read-request'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)
        response_json = response.json()
        task_id = response_json['response']['taskId']
    
        # get task id status
        time.sleep(1)  # wait for a second to receive the file name
        task_result = check_task_id_output(task_id, dnac_jwt_token)
        file_info = json.loads(task_result['progress'])
        file_id = file_info['fileId']
    
        # get output from file
        time.sleep(2)  # wait for two seconds for the file to be ready
        file_output = get_content_file_id(file_id, dnac_jwt_token)
        command_responses = file_output[0]['commandResponses']
        if command_responses['SUCCESS'] is not {}:
            command_output = command_responses['SUCCESS'][command]
        elif command_responses['FAILURE'] is not {}:
            command_output = command_responses['FAILURE'][command]
        else:
            command_output = command_responses['BLACKLISTED'][command]
        return command_output

class get_all_configsControllerSchema(Schema):
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_all_configsController(MethodResource, Resource):
    @doc(description="get_all_configs", tags=["DNAC API's"])
    @use_kwargs(get_all_configsControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/network-device/config'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        config_json = response.json()
        config_files = config_json['response']
        return config_files

class get_device_configControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_configController(MethodResource, Resource):
    @doc(description="get_device_config", tags=["DNAC API's"])
    @use_kwargs(get_device_configControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_name = kwargs.get("device_name", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        device_id = get_device_id_name(device_name, dnac_jwt_token)
        url = DNAC_URL + '/api/v1/network-device/' + device_id + '/config'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        config_json = response.json()
        config_file = config_json['response']
        return config_file

class check_ipv4_addressControllerSchema(Schema):
    ipv4_address = fields.String(required=True, description="ipv4_address is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class check_ipv4_addressController(MethodResource, Resource):
    @doc(description="check_ipv4_address", tags=["DNAC API's"])
    @use_kwargs(check_ipv4_addressControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        ipv4_address = kwargs.get("ipv4_address", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        # check against network devices interfaces
        try:
            device_info = check_ipv4_network_interface(ipv4_address, dnac_jwt_token)
            return True
        except:
            # check against any hosts
            try:
                client_info = get_client_info(ipv4_address, dnac_jwt_token)
                if client_info is not None:
                    return True
            except:
                pass
        return False
    
    
    

class check_ipv4_address_configsControllerSchema(Schema):
    ipv4_address = fields.String(required=True, description="ipv4_address is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class check_ipv4_address_configsController(MethodResource, Resource):
    @doc(description="check_ipv4_address_configs", tags=["DNAC API's"])
    @use_kwargs(check_ipv4_address_configsControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        ipv4_address = kwargs.get("ipv4_address", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/network-device/config'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        config_json = response.json()
        config_files = config_json['response']
        for config in config_files:
            run_config = config['runningConfig']
            if ipv4_address in run_config:
                return True
        return False

class check_ipv4_duplicateControllerSchema(Schema):
    config_file = fields.String(required=True, description="config_file is required ", example="00000")

class check_ipv4_duplicateController(MethodResource, Resource):
    @doc(description="check_ipv4_duplicate", tags=["DNAC API's"])
    @use_kwargs(check_ipv4_duplicateControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        config_file = kwargs.get("config_file", "10001")

        # open file with the template
        cli_file = open(config_file, 'r')
    
        # read the file
        cli_config = cli_file.read()
    
        ipv4_address_list = utils.identify_ipv4_address(cli_config)
    
        # get the DNA Center Auth token
    
        dnac_token = get_dnac_jwt_token(DNAC_AUTH)
    
        # check each address against network devices and clients database
        # initialize duplicate_ip
    
        duplicate_ip = False
        for ipv4_address in ipv4_address_list:
    
            # check against network devices interfaces
    
            try:
                device_info = check_ipv4_network_interface(ipv4_address, dnac_token)
                duplicate_ip = True
            except:
                pass
    
            # check against any hosts
    
            try:
                client_info = get_client_info(ipv4_address, dnac_token)
                if client_info is not None:
                    duplicate_ip = True
            except:
                pass
    
        if duplicate_ip:
            return True
        else:
            return False

class get_device_healthControllerSchema(Schema):
    device_name = fields.String(required=True, description="device_name is required ", example="00000")
    epoch_time = fields.String(required=True, description="epoch_time is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_device_healthController(MethodResource, Resource):
    @doc(description="get_device_health", tags=["DNAC API's"])
    @use_kwargs(get_device_healthControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_name = kwargs.get("device_name", "10001")
        epoch_time = kwargs.get("epoch_time", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        #device_id = get_device_id_name(device_name, dnac_jwt_token)
        device_id = ""
        url = DNAC_URL + '/api/v1/network-device'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        all_device_response = requests.get(url, headers=header, verify=False)
        device_list = all_device_response.json()
                
        for device in device_list['response']:
            if device['hostname'] == device_name:
                device_id = device['id']
        
        url = DNAC_URL + '/dna/intent/api/v1/device-detail?timestamp=' + str(epoch_time) + '&searchBy=' + device_id
        url += '&identifier=uuid'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        device_detail_json = response.json()
        device_detail = device_detail_json['response']
        return device_detail

class pnp_get_device_countControllerSchema(Schema):
    device_state = fields.String(required=True, description="device_state is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class pnp_get_device_countController(MethodResource, Resource):
    @doc(description="pnp_get_device_count", tags=["DNAC API's"])
    @use_kwargs(pnp_get_device_countControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_state = kwargs.get("device_state", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/dna/intent/api/v1/onboarding/pnp-device/count'
        payload = {'state': device_state}
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, data=json.dumps(payload), verify=False)
        pnp_device_count = response.json()
        return pnp_device_count['response']

class pnp_get_device_listControllerSchema(Schema):
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class pnp_get_device_listController(MethodResource, Resource):
    @doc(description="pnp_get_device_list", tags=["DNAC API's"])
    @use_kwargs(pnp_get_device_listControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/dna/intent/api/v1/onboarding/pnp-device'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        pnp_device_json = response.json()
        return pnp_device_json

class pnp_claim_ap_siteControllerSchema(Schema):
    device_id = fields.String(required=True, description="device_id is required ", example="00000")
    floor_id = fields.String(required=True, description="floor_id is required ", example="00000")
    rf_profile = fields.String(required=True, description="rf_profile is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class pnp_claim_ap_siteController(MethodResource, Resource):
    @doc(description="pnp_claim_ap_site", tags=["DNAC API's"])
    @use_kwargs(pnp_claim_ap_siteControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_id = kwargs.get("device_id", "10001")
        floor_id = kwargs.get("floor_id", "10001")
        rf_profile = kwargs.get("rf_profile", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        payload = {
            "type": "AccessPoint",
            "siteId": floor_id,
            "deviceId": device_id,
            "rfProfile": rf_profile
            }
        url = DNAC_URL + '/dna/intent/api/v1/onboarding/pnp-device/site-claim'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.post(url, headers=header, data=json.dumps(payload), verify=False)
        claim_status_json = response.json()
        claim_status = claim_status_json['response']
        return claim_status

class pnp_delete_provisioned_deviceControllerSchema(Schema):
    device_id = fields.String(required=True, description="device_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class pnp_delete_provisioned_deviceController(MethodResource, Resource):
    @doc(description="pnp_delete_provisioned_device", tags=["DNAC API's"])
    @use_kwargs(pnp_delete_provisioned_deviceControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_id = kwargs.get("device_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/dna/intent/api/v1/onboarding/pnp-device/' + device_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.delete(url, headers=header, verify=False)
        delete_status = response.json()
        return delete_status

class pnp_get_device_infoControllerSchema(Schema):
    device_id = fields.String(required=True, description="device_id is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class pnp_get_device_infoController(MethodResource, Resource):
    @doc(description="pnp_get_device_info", tags=["DNAC API's"])
    @use_kwargs(pnp_get_device_infoControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        device_id = kwargs.get("device_id", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/onboarding/pnp-device/' + device_id
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        device_info_json = response.json()
        device_info = device_info_json['deviceInfo']
        return device_info

class get_physical_topologyControllerSchema(Schema):
    ip_address = fields.String(required=True, description="ip_address is required ", example="00000")
    dnac_jwt_token = fields.String(required=True, description="dnac_jwt_token is required ", example="00000")

class get_physical_topologyController(MethodResource, Resource):
    @doc(description="get_physical_topology", tags=["DNAC API's"])
    @use_kwargs(get_physical_topologyControllerSchema, location=('json'))
    def post(self, **kwargs):
        DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
        ip_address = kwargs.get("ip_address", "10001")
        dnac_jwt_token = kwargs.get("dnac_jwt_token", "10001")
    
        url = DNAC_URL + '/api/v1/topology/physical-topology'
        header = {'content-type': 'application/json', 'x-auth-token': dnac_jwt_token}
        response = requests.get(url, headers=header, verify=False)
        topology_json = response.json()['response']
        topology_nodes = topology_json['nodes']
        topology_links = topology_json['links']
    
        # try to identify the physical topology
        for link in topology_links:
            try:
                if link['startPortIpv4Address'] == ip_address:
                    connected_port = link['endPortName']
                    connected_device_id = link['target']
                    for node in topology_nodes:
                        if node['id'] == connected_device_id:
                            connected_device_hostname = node['label']
                    break
            except:
                connected_port = None
                connected_device_hostname = None
        return connected_device_hostname, connected_port
    
    
    # dnac_token =  get_dnac_jwt_token(DNAC_AUTH)
    
    # print(get_physical_topology('10.93.130.21', dnac_token))
