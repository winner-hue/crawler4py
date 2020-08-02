def get_plugin_path(setting, path):
    try:
        path = setting.get("plugins").get(path)
    except AttributeError:
        path = None

    return path
