import os
from pick import pick
import shutil
import requests
from tqdm import tqdm
import zipfile
from datetime import datetime
import patches

if not os.path.exists("backups"):
    os.mkdir("backups")


def BackupMain():
    options = [
        "Restore from Backup",
        "Launch backup",
        "Take a backup",
        "Download a version from roblox's CDN",
    ]
    option, index = pick(options, "Select an option")
    if option == "Take a backup":
        Takebackup()
    if option == "Restore from Backup":
        Restore()
    if option == "Launch backup":
        LaunchBackup()
    if option == "Download a version from roblox's CDN":
        LaunchFromSetup()


def Takebackup():
    print("Taking a backup. Please wait!")
    version = patches.GetRobloxVersion("/Applications/Roblox.app/Contents/Info.plist")
    if os.path.exists("backups/" + "Roblox-" + version + ".backup"):
        print("A backup already exists for this version")
        return
    shutil.copytree("/Applications/Roblox.app", f"backups/Roblox-{version}.backup")
    print("Success")


def Restore():
    options = os.listdir("backups")
    option, index = pick(options, "Select a backup to restore to")
    print(f"Restoring from {option}")
    if os.path.exists("/Applications/Roblox.app"):
        shutil.rmtree("/Applications/Roblox.app")
        print("Removed current roblox install")
    shutil.copytree("backups/" + option, "backups/Roblox.app")
    shutil.move("backups/Roblox.app", "/Applications/Roblox.app")
    print("Restore complete")


def LaunchBackup():
    options = os.listdir("backups")
    option, index = pick(options, "Select a backup to launch")
    shutil.copytree(f"backups/{option}", "launch_backup_temp")
    os.system(
        "chmod +x launch_backup_temp/Contents/MacOS/RobloxPlayer"
    )  # fix permission denied
    os.system(
        "chmod +x launch_backup_temp/Contents/MacOS/RobloxCrashHandler"
    )  # fix crashing
    print(
        f"""
    If the backup is crashing then try the following
    
    1. Launch terminal and run the following commands :
        -> cd
        -> chmod +x RobloxPlayer
        -> chmod +x RobloxCrashHandler
    
    Roblox is currently launching. It may take a few seconds to launch
    """
    )
    os.system("launch_backup_temp/Contents/MacOS/RobloxPlayer")
    shutil.rmtree("launch_backup_temp")


def LaunchFromSetup():
    print("Getting version from Roblox CDN. Please wait")
    k = patches.get_versions(datetime.now().year, datetime.now().month)
    if k == None:
        print(
            "An error occurred while getting the version. Please check your internet connection"
        )
        return
    options = []
    for version, date in k:
        options.append(f"{version} - {date}")
    option, index = pick(
        options, "Select a version to download (note: Some may not work)"
    )
    version = option.split(" ")[0]
    url = f"https://setup.rbxcdn.com/mac/{version}-RobloxPlayer.zip"
    print(f"Downloading version {version} (url: {url})")

    response = requests.get(
        url=url,
        stream=True,
        allow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
        },
    )
    if response.status_code != 200:
        print(f"Error downloading file: {response.status_code}")
        return
    total_size = int(response.headers.get("content-length", 0))
    progress_bar = tqdm(
        total=total_size, unit="B", unit_scale=True, desc="Downloading client"
    )
    with open("RobloxDowngrade.zip", "wb") as file:
        for data in response.iter_content(1024):
            progress_bar.update(len(data))
            if not data:
                break
            file.write(data)
    progress_bar.close()

    print("Extracting the client")
    with zipfile.ZipFile("RobloxDowngrade.zip", "r") as zip_ref:
        zip_ref.extractall(f"client")
        print("Extracted")
    shutil.move("client/RobloxPlayer.app", f"backups/RobloxDownload-{version}.backup")
    os.remove("RobloxDowngrade.zip")
    shutil.rmtree("client")
    print("You can now launch the client using 'Launch backup'")
