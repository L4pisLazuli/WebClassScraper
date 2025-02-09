import requests
import re

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.acs = {"acs_": "12345678"}
        self.cookie = None

    def login(self, url, login_info, logger):
        if url is None:
            logger.error("URL is unset")
            return None, None, None
        if not login_info.get("username") or not login_info.get("val"):
            logger.error("Username or Password are unset")
            return None, None, None
        try:
            acs_url = f"{url}/webclass/login.php"
            response = self.session.post(acs_url, data=login_info)
            acs_value = re.findall(r'acs_=([a-zA-Z0-9]+)', response.text)[-1]
            self.acs = {"acs_": acs_value}
            self.cookie = {"WBT_Session": response.cookies.get('WBT_Session')}
            logger.info("login success")
            return self.session, self.acs, self.cookie
        except Exception as e:
            logger.error(f"login failed: {e}")
            return None, None, None

    def set_wbt_session(self, wbt_session, logger):
        self.cookie = {"WBT_Session": wbt_session}
        logger.info("set wbt_session success")
        return self.cookie

    def logout(self, url, logger):
        if url is None or self.cookie is None:
            logger.error("did not login")
            return False
        logout_url = f"{url}/webclass/logout.php"
        self.session.get(logout_url, cookies=self.cookie)
        self.__init__()
        logger.info("logout success")
        return True