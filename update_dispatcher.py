import subprocess
import time

import requests
import os
import shutil
import sys
from zipfile import ZipFile
from executor import check_and_kill_process, execute_application
from logger import write_log

API = "https://aptitudealchemy.pythonanywhere.com/"
SOFTWARE_UPDATE_API = API + 'software/update/get_new_version'
UPDATE_FOLDER = os.path.join(os.curdir, 'update')
CURRENT_VERSION = None
LATEST_UPDATE = None
ENV_KEY = "aptitude_alchemy_version"

USERNAME = os.getenv('USERNAME')

STARTUP_PATH = f"C:\\Users\\{USERNAME}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"

def check_latest_version():
    global LATEST_UPDATE
    try:
        response = requests.get(SOFTWARE_UPDATE_API)

        if not response.status_code == 200:
            return False

        json_data = response.json()
        LATEST_UPDATE = json_data[-1]
        LATEST_UPDATE.update({'version': json_data[-1].get('version').replace(".zip", "")})

        if CURRENT_VERSION == LATEST_UPDATE.get('version'):
            write_log("Already latest version is installed.")
            # sys.exit(0)
            return

        write_log("New update {0} is available".format(LATEST_UPDATE.get('version')))
        return True

    except ConnectionError as connection_error:
        write_log(connection_error, 'connection error')

    except Exception as exception:
        write_log(exception, 'exception')

    return False

def download_update():
    # print("Downloading update...")
    write_log("Downloading update...")
    check_and_kill_process()

    try:

        if LATEST_UPDATE is None:
            print("Update not found")
            return

        url = LATEST_UPDATE.get('url')
        response = requests.get(url)

        if not response.status_code == 200:
            write_log("Unable to download the update right now!", 'error')
            return

        if not os.path.exists(UPDATE_FOLDER):
            os.mkdir(UPDATE_FOLDER)
            write_log("Update folder is created.")

        file_name = url.split('/')[-1]
        path_to_save = os.path.join(UPDATE_FOLDER, file_name)

        with open(path_to_save, 'wb') as file:
            file.write(response.content)

            if not os.path.exists(path_to_save):
                write_log("Unable to download the latest release.", 'error')
                return

            write_log("Latest release is downloaded successfully")
            set_version_env(LATEST_UPDATE.get('version'))
            print(get_current_version())
            extract_update(path_to_save)

    except ConnectionError as connection_error:
        write_log(connection_error, 'connection error')

    except Exception as exception:
        write_log(exception, 'exception')

def extract_update(path):
    try:
        extract_folder = UPDATE_FOLDER

        with ZipFile(path, 'r') as update:
            write_log("Extracting update...")
            update.extractall(extract_folder)
            write_log("Update extracted")

        move_to_startup(extract_folder + '\\test-dist-updates-{0}'.format(LATEST_UPDATE.get('url').split('/')[-1].replace('.zip', '')) + '\\main.exe')

    except Exception as e:
        write_log(e, 'exception')

def move_to_startup(file):

    if os.path.exists(file):

        if os.path.exists(STARTUP_PATH + '\\main.exe'):
            os.remove(STARTUP_PATH + '\\main.exe')
            write_log("Old file was removed.")

        shutil.move(file, STARTUP_PATH)
        write_log("File moved")

def main():

    if not check_latest_version():
        write_log("Something went wrong!", 'error')
        return

    download_update()

    if os.path.exists(UPDATE_FOLDER):
        shutil.rmtree(UPDATE_FOLDER)
        write_log("Update folder is removed.")

    execute_application(STARTUP_PATH)

def get_current_version():
    return os.getenv(ENV_KEY)

def set_version_env(value):
    subprocess.run(['setx', ENV_KEY, value])


if __name__ == '__main__':

    if get_current_version() is None:
        set_version_env('0.0.0')

    while True:

        version = get_current_version()
        CURRENT_VERSION = version

        main()
        time.sleep(3600 * 5) # Checks for new update every 5 hours
