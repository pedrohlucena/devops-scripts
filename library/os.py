import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Os:
    def __init__(self):
        self.repos_folder_path = os.getenv('REPOS_FOLDER_PATH')

    def go_to_repo(self, repository_name):
        os.chdir(
            os.path.join(self.repos_folder_path, repository_name)
        )

    def stay_in_the_current_dir():
        os.system("/bin/bash")