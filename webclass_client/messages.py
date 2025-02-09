import re
from datetime import datetime

def get_lecture_message(url, lecture_id, acs, cookie, session, date, logger):
    date_format = "%Y-%m-%d %H:%M:%S"
    date_obj = datetime.strptime(f"{date} 00:00:00", date_format)
    if url is None or cookie is None:
        logger.error("did not login")
        return []
    lecture_message = []
    login_url = f"{url}/webclass/course.php/{lecture_id}/login?acs_={acs['acs_']}"
    acs_html = session.post(login_url, data=acs, cookies=cookie)
    acs["acs_"] = re.findall(r'acs_=([a-zA-Z0-9]+)', acs_html.text)[-1]
    messages_url = f"{url}/webclass/course.php/{lecture_id}/api/timeline/messages?head=0&filter=false&newer_than={date_obj.strftime('%Y-%m-%d+%H:%M:%S')}"
    output = session.get(messages_url, cookies=cookie).json()
    for record in output.get("records", []):
        message = record.get("message")
        lecture_message.append(message)
    logger.info(f"found {len(lecture_message)} messages")
    return lecture_message