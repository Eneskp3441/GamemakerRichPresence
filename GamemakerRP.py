"""
---------------------- BY Eneskp#3441 ----------------------


"""
import psutil, os, json, time, glob
from pypresence import Presence
from datetime import datetime
import PIL.Image, threading
from pystray import Icon as strayicon, Menu, MenuItem



# Discord Presence
client_id = "1062461019458379937"

programActive = True
rpcData = None
lastEditing = None
settingsSaveFolder = os.getenv('APPDATA')+"\\GamemakerRichPresence"
if not os.path.exists(settingsSaveFolder):
    os.makedirs(settingsSaveFolder)
userSettingsPath = settingsSaveFolder+"\\userSettings.json"

programPath = current_dir = os.path.dirname(os.path.abspath(__file__))
programIconPath = os.path.join(current_dir, "icon.png")

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
        icon.stop()
        programActive = False
        if not icon_thread.is_alive():
            icon_thread.join()
    elif str(item) == "Reset":
        os.remove(userSettingsPath)
        userSettings = getUserSettings()
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
    MenuItem("Settings", settingsMenu), 
    MenuItem("Exit", on_clicked)
    )

icon.menu = mainMenu
def runStray():
    global icon
    icon.run()



icon_thread = threading.Thread(target=runStray)
icon_thread.daemon = True
icon_thread.start()

time.sleep(1)

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
while programActive:
    try:
        gamemakerIsRunning = "GameMaker.exe" in (p.name() for p in psutil.process_iter())
    except:
        gamemakerIsRunning = False
    if gamemakerIsRunning:
        projectFolder = ""
        rpcData = {"state" : ""}
        lastEditPath = ""
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
        try:RPC.update(**rpcData)
        except: pass
    else:
        lastProjectName = ""
        currentTimeStamp = -1
        try:RPC.clear()
        except: pass
    
    
    time.sleep(3)
   

try:RPC.close()
except: pass