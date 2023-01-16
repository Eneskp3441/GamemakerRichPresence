import requests, sys, psutil, time, os,subprocess, json
from datetime import datetime

url = 'https://api.github.com/repos/Eneskp3441/GamemakerRichPresence/releases'
headers = {
    'Authorization': 'Token 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',
    'Accept': 'application/vnd.github+json'
}
applicationPath = "C:\\Program Files (x86)\\Gamemaker Rich Presence\\Gamemaker RichPresence.exe"
settingsSaveFolder = os.getenv('APPDATA')+"\\GamemakerRichPresence"

def log(message):
    logs_path = os.path.join(settingsSaveFolder, 'logs')
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(logs_path, f'{today}.log')
    if not os.path.exists(log_file):
        open(log_file, 'w').close()
    with open(log_file, 'a') as f:
        f.write(f'{datetime.now()} - {message}\n')


def close_app(app_name):
    for process in psutil.process_iter():
        try:
            process_name = process.name()
            if process_name == app_name:
                try:
                    process.terminate()
                    subprocess.run(["taskkill", "/F", "/IM", app_name],timeout=3)
                    print(f"{app_name} closed.")
                except Exception as e:
                    log(" #1018 Update Checker; application close problem" + str(e))
                return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"{app_name} not running.")

if len(sys.argv) > 1:
    if sys.argv[1] == "--update":
        close_app("Gamemaker RichPresence.exe")
        time.sleep(2)
        selectedData = None
        response = requests.get(url, headers=headers)
        data = response.json()
        for release in data:
            if release['tag_name'] == "Directly":
                selectedData = release
                break
        try:
            if selectedData != None:
                releaseVersion = json.loads(selectedData['body'])['version']
                assets = selectedData['assets'][0]
                download_url = assets['browser_download_url']
                response = requests.get(download_url)
                open(applicationPath, "wb").write(response.content)
                print("Application updated!")
                subprocess.run([applicationPath, "--updated"], shell=True,timeout=3)
            else:
                log(" #1008 Update Checker data not found")
                subprocess.run([applicationPath, "--updatefailed"], shell=True,timeout=3)
                print("Repo not found")
        except subprocess.TimeoutExpired as e:
            log(" #1012 Update Checker Timeout ")
        except Exception as e:
            log(" #1010 Update Checker Create Application Problem: " + str(e))
            subprocess.run([applicationPath, "--updatefailed"], shell=True,timeout=3)
            print("Update failed: ", e)
        finally:
            sys.exit(0)
