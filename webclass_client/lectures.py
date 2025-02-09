from bs4 import BeautifulSoup as bs4
import re

def get_lecture_id_list(url, acs, cookie, session, logger):
    if url is None or cookie is None:
        logger.error("did not login")
        return []
    lecture_id_list = []
    req_url = f"{url}/webclass/?acs_={acs['acs_']}"
    response = session.get(req_url, data=acs, cookies=cookie)
    response.encoding = response.apparent_encoding
    if len(response.text) <= 1000:
        logger.error("login failed")
        return []
    soup = bs4(response.text, "html.parser")
    table = soup.find("table")
    if table is None:
        logger.error("login data is invalid")
        return lecture_id_list
    links = table.find_all(href=re.compile("/webclass/course.php/"))
    if len(links) == 0:
        logger.error("lecture not found")
        return []
    acs_found = re.findall(r'acs_=([a-zA-Z0-9]+)', str(links[0]))
    if acs_found:
        acs["acs_"] = acs_found[-1]
    for link in links:
        ids = re.findall(r'([a-zA-Z0-9]+)', link.contents[0])
        if ids:
            lecture_id_list.append(ids[-1])
    return lecture_id_list

def get_lecture_info(url, lecture_id, acs, cookie, session, logger):
    if url is None or cookie is None:
        logger.error("did not login")
        return {}
    lecture_info = {}
    login_url = f"{url}/webclass/course.php/{lecture_id}/login?acs_={acs['acs_']}"
    acs_html = session.post(login_url, data=acs, cookies=cookie)
    acs["acs_"] = re.findall(r'acs_=([a-zA-Z0-9]+)', acs_html.text)[-1]
    course_url = f"{url}/webclass/course.php/{lecture_id}/?acs_={acs['acs_']}"
    response = session.get(course_url, data=acs, cookies=cookie)
    response.encoding = response.apparent_encoding
    if len(response.text) <= 1000:
        logger.error("login failed")
        return {}
    soup = bs4(response.text, "html.parser")
    target_container = soup.find("div", class_="col-xs-12 col-sm-8 col-md-9 col-lg-10")
    if not target_container:
        logger.error("lecture info container not found")
        return {}
    sections = target_container.find_all("section", class_="panel panel-default cl-contentsList_folder")
    for i, section in enumerate(sections):
        section_title = section.find("h4", class_="panel-title")
        section_name = section_title.text if section_title and section_title.text != '' else f"section{i}"
        content_dict = {}
        j = 0
        for content in section.find_all("section", "list-group-item cl-contentsList_listGroupItem"):
            for item in content.find_all("div", class_="cl-contentsList_content"):
                item_dict = {}
                item_name = item.find("h4", "cm-contentsList_contentName").text.replace("New", "").replace("\n", "")
                item_category = item.find("div", "cl-contentsList_categoryLabel").text
                period_array = item.find_all("div", "cm-contentsList_contentDetailListItemData")
                try:
                    if period_array:
                        item_availability_period = period_array[-1].text
                    else:
                        item_availability_period = None
                except Exception as e:
                    logger.error(f"error: {e}")
                    item_availability_period = None
                if item_availability_period:
                    splits = item_availability_period.split(" - ")
                    period_from = splits[0].lstrip()
                    period_to = splits[1].lstrip() if len(splits) > 1 else None
                else:
                    period_from = None
                    period_to = None
                item_dict["name"] = item_name
                item_dict["category"] = item_category
                item_dict["availability_period_from"] = period_from
                item_dict["availability_period_to"] = period_to
                content_dict[f"item{j}"] = item_dict
                j += 1
        lecture_info[section_name] = content_dict
    return lecture_info

def get_lecture_name(url, lecture_id, acs, cookie, session, logger):
    if url is None or cookie is None:
        logger.error("did not login")
        return None
    req_url = f"{url}/webclass/?acs_={acs['acs_']}"
    response = session.get(req_url, data=acs, cookies=cookie)
    response.encoding = response.apparent_encoding
    if len(response.text) <= 1000:
        logger.error("login failed")
        return None
    soup = bs4(response.text, "html.parser")
    for lecture in soup.find_all("a", href=re.compile("/webclass/course.php/")):
        name = lecture.contents[0].lstrip('»').strip()
        if lecture_id in name:
            return name
    logger.error("lecture not found")
    return None
