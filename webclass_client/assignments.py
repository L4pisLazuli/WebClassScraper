from datetime import datetime
from .lectures import get_lecture_name, get_lecture_info, get_lecture_id_list

def get_assignment_info(url, acs, cookie, session, date, logger):
    lecture_id_list = get_lecture_id_list(url, acs, cookie, session, logger)
    if not lecture_id_list:
        logger.error("lecture not found")
        return []
    assignment_info = []
    date_format = "%Y/%m/%d %H:%M"
    date_obj = datetime.strptime(date.strftime(date_format), date_format)
    for lecture_id in lecture_id_list:
        lecture_name = get_lecture_name(url, lecture_id, acs, cookie, session, logger)
        lecture_info = get_lecture_info(url, lecture_id, acs, cookie, session, logger)
        for section in lecture_info:
            for key in lecture_info[section]:
                item = lecture_info[section][key]
                start = item.get("availability_period_from")
                deadline = item.get("availability_period_to")
                if not start or not deadline:
                    continue
                try:
                    start_dt = datetime.strptime(start, date_format)
                    deadline_dt = datetime.strptime(deadline, date_format)
                except Exception as e:
                    logger.error(f"Error parsing dates: {e}")
                    continue
                if deadline_dt > date_obj > start_dt and item["category"] not in ["資料"]:
                    item["subject"] = lecture_name
                    assignment_info.append(item)
    logger.info(f"found {len(assignment_info)} assignments")
    return assignment_info