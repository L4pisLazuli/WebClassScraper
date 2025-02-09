from webclass_client import WebClassClient
from datetime import datetime

if __name__ == "__main__":
    url = "https://els.sa.dendai.ac.jp"
    username = "your_username"
    password = "your_password"

    client = WebClassClient(url)
    client.set_login_info(username, password)
    if client.login():
        lecture_ids = client.get_lecture_id_list()
        print("Lecture IDs:", lecture_ids)

        assignment_info = client.get_assignment_info(datetime.now())
        print("Assignment Info:", assignment_info)

        for lecture_id in lecture_ids:
            messages = client.get_lecture_message(lecture_id, "2000-01-01")
            print(f"Messages for lecture {lecture_id}:")
            for msg in messages:
                print(msg)

        client.logout()
    else:
        print("Login failed.")
