
from datetime import datetime
from django.forms.models import model_to_dict

from utils.time_utils import datetime_to_str


class Base(object):

    def to_json(self):
        json_data = model_to_dict(self)
        for key in json_data.keys():
            value = json_data[key]
            if isinstance(value, datetime):
                json_data[key] = datetime_to_str(value)
        return json_data
