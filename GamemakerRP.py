"""
---------------------- BY Eneskp#3441 ----------------------


"""
import psutil, os, json, time, glob,requests,subprocess,sys
from pypresence import Presence
import PIL.Image, threading
from pystray import Icon as strayicon, Menu, MenuItem
from datetime import datetime
import win32gui
import win32process

VERSION = "1.0.0"
UPDATEURL = 'https://api.github.com/repos/Eneskp3441/GamemakerRichPresence/releases'
headers = {
    'Authorization': 'Token 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',
    'Accept': 'application/vnd.github+json'
}
# Discord Presence
client_id = "1062461019458379937"
programActive = True
rpcData = None
lastEditing = None
latestVersion = VERSION
settingsSaveFolder = os.getenv('APPDATA')+"\\GamemakerRichPresence"
if not os.path.exists(settingsSaveFolder):
    os.makedirs(settingsSaveFolder)
userSettingsPath = settingsSaveFolder+"\\userSettings.json"

programPath = os.path.abspath(os.getcwd())
current_dir = os.path.dirname(os.path.abspath(__file__))
programIconPath = os.path.join(current_dir, "icon.png")



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

log("Application Started!")

def getUserSettings():
    if os.path.exists(userSettingsPath):
        with open(userSettingsPath, "r") as f:
            return json.load(f)
    else:
        data = {
            "showProjectName" : True,
            "showEditingName" : True,
            "enableObjects" : True,
            "enableRooms" : True,
            "enableScripts" : True,
            "enableSounds" : True,
            "enableSprites" : True,
            "enableTilesets" : True,
            "enableAnimcurves" : True,
            "enableFonts" : True,
            "enableSequences" : True,
            "enableExtensions" : True,
            "enableNotes" : True,
            "enablePaths" : True,
            "enableShaders" : True,
            "enableTimelines" : True,
        }
        setUserSettings(data)
        return data

def setUserSettings(data):
    with open(userSettingsPath, "w") as f:
        return json.dump(data, f)


currentTimeStamp = -1
folder_paths = ['objects', 'rooms', 'scripts', 'sounds', 'sprites', 'tilesets', 'animcurves', 'fonts', 'sequences', 'extensions', 'notes', 'paths', 'shaders', 'timelines']
userSettings = getUserSettings()





def get_latest_file(folder):
    all_files = []
    for folder_path in folder_paths:
        if os.path.exists(folder + "\\" + folder_path):
            files = glob.glob(folder + "\\" + folder_path + '\\*')
            if files:
                files.sort(key=os.path.getmtime, reverse=True)
                all_files.extend(files)

    all_files.sort(key=os.path.getmtime, reverse=True)
    if len(all_files) > 0:
        return all_files[0]
    else:
        return False

def closeApp():
    global icon,programActive
    icon.stop()
    programActive = False
    if not icon_thread.is_alive():
        icon_thread.join()

IDEVersion   = ""

userPath = os.path.expandvars(r'%AppData%\GameMakerStudio2')
userName = ""

with open(userPath+r'\um.json', 'r') as f:
    data = json.load(f)
    userName = data["login"].rsplit("@")[0]

recentProjects = None

for file in os.listdir(userPath):
     if file.startswith(userName):
        recentProjects = userPath+'\\'+file+'\\'+'recent_projects'
        break


def on_clicked(icon, item):
    global programActive,icon_thread,userSettings
    name = "".join(str(item).split())
    name = name[0].lower() + name[1:]

    if str(item) == "Exit":
        closeApp()
    elif str(item) == "Reset":
        os.remove(userSettingsPath)
        userSettings = getUserSettings()
    elif str(item) == "Update":
        try:
            closeApp()
            print("App closing..")
            subprocess.run([programPath+"\\UpdateChecker.exe", "--update"],shell=True,timeout=3)
            
        except Exception as e:
            log(" #1000 Rich Presence Update Failed " + str(e) + " " + programPath+"\\UpdateChecker.exe")
            icon.notify("Gamemaker - Rich Presence Update Failed", title="UpdateChecker Not Found " + str(e))

    else:
        userSettings[name] = not userSettings[name]
        setUserSettings(userSettings)


def checkCheck(item):
    name = "".join(str(item).split())
    name = name[0].lower() + name[1:]

    return userSettings[name]

icon = strayicon('Gamemaker - Rich Presence', icon=PIL.Image.open(programIconPath))

menu_items = []

menu_items.append(MenuItem( 'Show Project Name', on_clicked, checked=lambda item: userSettings["showProjectName"]))
menu_items.append(MenuItem( 'Show Editing Name', on_clicked, checked=lambda item: userSettings["showEditingName"]))

for i in userSettings.keys():
    if i.startswith("enable"):
        itemName = i.replace("enable", "Enable ").title()
        item = MenuItem(itemName, on_clicked, checked=checkCheck)
        menu_items.append(item)

menu_items.append(MenuItem( 'Reset', on_clicked))

settingsMenu = Menu(*menu_items)

mainMenu = Menu(
    MenuItem("Update", on_clicked,visible=lambda item: latestVersion != VERSION),
    MenuItem("Settings", settingsMenu), 
    MenuItem("Exit", on_clicked)
    )

icon.menu = mainMenu
def runStray():
    global icon
    icon.run()

def checkUpdate():
    global latestVersion,icon
    while 1:
        print("Update Checking..")
        try:
            selectedData = None
            response = requests.get(UPDATEURL,headers=headers)
            data = response.json()
            for release in data:
                if release['tag_name'] == "Directly":
                    selectedData = release
                    break

            if selectedData != None:
                __data = json.loads(selectedData['body'])['version']
                latestVersion = __data
                if latestVersion != VERSION:
                    icon.update_menu()
                    icon.notify("Update Available!", "Gamemaker Rich Presence")
                    break
            
        except Exception as e:
            log(" #1002 Check Update Failed " + str(e))
            print("Error Check Update: ", e)
        time.sleep(1 * 60 * 60)
    


def list_windows(pid):
    try:
        def callback(hwnd, hwnds):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        for hwnd in hwnds:
            name = win32gui.GetWindowText(hwnd)
            if "GameMaker"  in name:
                return name
    except Exception as e:
        log(" #1024 List Windows Error " + str(e))


icon_thread = threading.Thread(target=runStray)
icon_thread.daemon = True
icon_thread.start()

update_thread = threading.Thread(target=checkUpdate)
update_thread.daemon = True
update_thread.start()

time.sleep(1)
if len(sys.argv) > 1 and sys.argv[1] == "--updated":
    icon.notify("Gamemaker - Rich Presence Updated!", title="Gamemaker - Rich Presence By Eneskp#3441")

elif len(sys.argv) > 1 and sys.argv[1] == "--updatefailed":
    icon.notify("Gamemaker - Rich Presence Update Failed!", title="Please download from github page")

elif latestVersion == VERSION:
    icon.notify("Gamemaker - Rich Presence Started!", title="Gamemaker - Rich Presence By Eneskp#3441")

while 1:
    try: 
        RPC = Presence(client_id)
        print("Discord Found")
        break
    except: 
        time.sleep(3)
        print("Discord Not Found")


RPC.connect()
projectName = ""
lastProjectName = ""
isStartPage = ""
while programActive:
    try:
        gamemakerIsRunning = False
        for p in psutil.process_iter(): 
            if p.name() == "GameMaker.exe":
                isStartPage = "Start Page" in list_windows(p.pid)
                gamemakerIsRunning = True
                break
    except Exception as e:
        print("Find window error: ", str(e))
        gamemakerIsRunning = False
    if gamemakerIsRunning:
        projectFolder = ""
        rpcData = {"state" : ""}
        lastEditPath = ""
        if not isStartPage:
            with open(recentProjects, 'r') as f:
                string = f.read()

                project = string.split("\n")[0]
                projectFolder = "\\".join(project.rsplit("\\")[:-1])
                projectName = project.rsplit("\\")[-1][:-4]

                if projectName != lastProjectName:
                    currentTimeStamp =  time.time()
                    lastProjectName = projectName

            lastEditPath = get_latest_file(projectFolder)
            if lastEditPath != False:
                editingType =  lastEditPath.rsplit("\\")[-2]
                with open(projectFolder+"\\"+projectName+".yyp", 'r') as f:
                    string = f.read()
                    string = string[string.find("\"IDEVersion\": \"")+15:]
                    string = string[:string.find('",')]
                    IDEVersion = string

                isVisible = True
                
                for i in userSettings.keys():
                    if i.startswith("enable"):
                        if not userSettings[i] and editingType == i.replace('enable', '').lower():
                            isVisible = False


                if ( not isVisible ):
                    rpcData["state"] = "Editing Project"
                    if userSettings['showProjectName']: rpcData['details'] = projectName
                    rpcData["large_image"] = "gamemaker"
                    rpcData["large_text"] = IDEVersion
                    if currentTimeStamp != -1: rpcData["start"] = currentTimeStamp
                else:
                    rpcData["state"] = "Editing " + ( lastEditPath.rsplit("\\")[-1] if userSettings['showEditingName'] else editingType[:-1])
                    if userSettings['showProjectName']: rpcData['details'] = projectName
                    rpcData["large_image"] = editingType
                    rpcData["small_image"] = "gamemaker"
                    rpcData["large_text"] = editingType[:-1]
                    rpcData["small_text"] = IDEVersion
                    if currentTimeStamp != -1: rpcData["start"] = currentTimeStamp
        else:
            rpcData["state"] = "Selecting Project.."
            rpcData["details"] = "Start Page"
            rpcData["large_image"] = "gamemaker"

        try:RPC.update(**rpcData)
        except Exception as e:
            log(" #1004 RPC Update failed " + str(e))
    else:
        lastProjectName = ""
        currentTimeStamp = -1
        try:RPC.clear()
        except Exception as e:
            log(" #1006 Rich Presence Clear Failed " + str(e))
    
    
    time.sleep(15)
   

try:RPC.close()
except: pass