try:
    from flask import Flask, render_template
    from flask_restful import Resource, Api
    from apispec import APISpec
    from marshmallow import Schema, fields
    from apispec.ext.marshmallow import MarshmallowPlugin
    from flask_apispec.extension import FlaskApiSpec
    from flask_apispec.views import MethodResource
    from flask_apispec import marshal_with, doc, use_kwargs

    from API.ClusterHealth.views import HealthController
    from API.ComplianceLite.views import ComplianceLite
    from API.ComplianceLite.views import WeatherController
    
    import requests
    import json
    import subprocess
    import version
    
except Exception as e:
    print("__init Modules are Missing {}".format(e))

app = Flask(__name__)  # Flask app instance initiated
app.config['SECRET_KEY'] = 'C1sc012345'
api = Api(app)  # Flask restful wraps Flask app around it.
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Compliance Lite',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)
