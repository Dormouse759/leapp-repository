from leapp.models import Model, fields
from leapp.topics import SystemInfoTopic


class PythonScl(Model):
    topic = SystemInfoTopic #  TODO: import appropriate topic and set it here
    scls = fields.JSON()
    pkgs = fields.JSON()
