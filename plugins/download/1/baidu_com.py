from download.request import request


def process(task_url, message):
    r = request.get(task_url)
    if r.status_code > 400:
        message["recovery_flag"] = message["recovery_flag"] + 1 if message["recovery_flag"] else 1
    else:
        if message.get("task_encode"):
            message["view_source"] = r.content.decode(message.get("task_encode"))
        else:
            message["view_source"] = r.text
    return message
