from .logger_setup import setup_logger
from .session_manager import SessionManager
from .lectures import get_lecture_id_list, get_lecture_info, get_lecture_name
from .assignments import get_assignment_info
from .messages import get_lecture_message


class WebClassClient:
    def __init__(self, url):
        self.url = url
        self.login_info = {"username": "", "val": ""}
        self.session_manager = SessionManager()
        self.acs = {"acs_": "12345678"}
        self.cookie = None
        self.logger = setup_logger(__name__)

    def set_login_info(self, username, password):
        self.login_info["username"] = username
        self.login_info["val"] = password

    def login(self):
        session, acs, cookie = self.session_manager.login(self.url, self.login_info, self.logger)
        if session is not None:
            self.acs = acs
            self.cookie = cookie
            return True
        return False

    def logout(self):
        return self.session_manager.logout(self.url, self.logger)

    def get_lecture_id_list(self):
        return get_lecture_id_list(self.url, self.acs, self.cookie, self.session_manager.session, self.logger)

    def get_lecture_info(self, lecture_id):
        return get_lecture_info(self.url, lecture_id, self.acs, self.cookie, self.session_manager.session, self.logger)

    def get_lecture_name(self, lecture_id):
        return get_lecture_name(self.url, lecture_id, self.acs, self.cookie, self.session_manager.session, self.logger)

    def get_assignment_info(self, date):
        return get_assignment_info(self.url, self.acs, self.cookie, self.session_manager.session, date,
                                   self.logger)

    def get_lecture_message(self, lecture_id, date="2000-01-01"):
        return get_lecture_message(self.url, lecture_id, self.acs, self.cookie, self.session_manager.session, date,
                                   self.logger)
