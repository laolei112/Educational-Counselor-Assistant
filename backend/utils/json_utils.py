import json
from datetime import datetime, date


class JsonDateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def json_dumps(data):
    return json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            sort_keys=True,
            cls=JsonDateEncoder)


def json_dumps_to_file(data, savepath):
    # json 的数字key 是会被转成字符串的，所以要合并
    merged_dict = {}
    for key, value in data.items():
        if isinstance(key, int):
            merged_dict[str(key)] = value
        else:
            merged_dict[key] = value
    with open(savepath, "wb+") as f:
        f.write(json_dumps(merged_dict).encode("utf-8"))


def json_loads_from_file(filepath):
    with open(filepath, "rb") as f:
        task_info = json.loads(f.read().decode("utf-8"))
    return task_info
