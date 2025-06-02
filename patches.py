import os
from tqdm import tqdm
import shutil
import re
import plistlib
import requests
from pick import pick
from subprocess import *
import psutil


def UninstallRoblox():
    options = [
        "Reset (will remove configs but not the app)",
        "App uninstall (will uninstall player and studio)",
    ]
    title = "Select what type"
    option, index = pick(options, title)
    if option == "Reset (will remove configs but not the app)":
        print("Resetting. Please wait!")
        shutil.rmtree(
            "/Applications/Roblox.app/Contents/MacOS/ClientSettings", ignore_errors=True
        )
        shutil.rmtree("~/Library/Roblox", ignore_errors=True)
        try:
            os.remove("~/Library/Preferences/com.Roblox.Roblox.plist")
            os.remove("~/Library/Preferences/com.roblox.RobloxPlayerChannel.plist")
            os.remove("~/Library/Preferences/com.roblox.RobloxPlayer.plist")
            os.remove("~/Library/Preferences/com.roblox.RobloxStudio.plist")
            os.remove("~/Library/Preferences/com.roblox.RobloxStudioChannel.plist")
        except:
            pass  # we dont really care lol
        shutil.rmtree("~/Library/Logs/Roblox", ignore_errors=True)
        shutil.rmtree(
            "~/Library/Saved Application State/com.Roblox.RobloxStudio.savedState",
            ignore_errors=True,
        )
        shutil.rmtree(
            "~/Library/Caches/com.Roblox.StudioBootstrapper", ignore_errors=True
        )
        print("Reset complete!")
    if option == "App uninstall (will uninstall player and studio)":
        shutil.rmtree("/Applications/Roblox.app", ignore_errors=True)
        shutil.rmtree("/Applications/RobloxStudio.app", ignore_errors=True)
        print("Deleted roblox successfully!")


def KillRoblox():
    for pid in (
        process.pid for process in psutil.process_iter() if process.name() == "Roblox"
    ):
        os.kill(pid, 0)


def KillRobloxInstaller():
    for pid in (
        process.pid
        for process in psutil.process_iter()
        if process.name() == "RobloxPlayerInstaller_patched"
    ):
        os.kill(pid, 0)


def install_studio():
    if os.path.exists("/Applications/Roblox.app"):
        print("Roblox is already installed. Re-installing roblox!")
        shutil.rmtree("/Applications/RobloxStudio.app")
    if os.path.exists("installer.dmg"):
        os.remove("installer.dmg")
    print("Downloading the roblox installer")
    # --- code from google gemini lol (added osx user-agent cuz roblox keeps downloading the Windows version)
    response = requests.get(
        "https://setup.rbxcdn.com/mac/RobloxStudio.dmg",
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
        total=total_size, unit="B", unit_scale=True, desc="Downloading installer"
    )
    with open("installer.dmg", "wb") as file:
        for data in response.iter_content(1024):
            progress_bar.update(len(data))
            if not data:
                break
            file.write(data)
    progress_bar.close()
    # -------------------------------
    if not os.path.exists("installer.dmg"):
        print("Error while downloading the roblox dmg")
        return
    print("Attempting to mount the DMG")
    k = os.system("hdiutil mount installer.dmg")
    if k != 0:
        print(f"Error while mounting the DMG : {k}")
        return
    print("Mounted the DMG")
    # start thread
    print("Launching the installer")
    installer_process = Popen(
        "/Volumes/RobloxStudioInstaller/RobloxStudioInstaller.app/Contents/MacOS/RobloxStudioInstaller"
    )
    completed = psutil.wait_procs([installer_process])
    if completed:
        print("Install completed successfully.")
    else:
        print("Installer timed out or failed.")
        installer_process.kill()
    print("Cleaning up")
    print("Unmounting the DMG")
    os.system("hdiutil detach /Volumes/RobloxStudioInstaller")
    print("Deleting the DMG")
    os.remove("installer.dmg")


def install():
    if os.path.exists("/Applications/Roblox.app"):
        print("Roblox is already installed. Re-installing roblox!")
        shutil.rmtree("/Applications/Roblox.app")
    if os.path.exists("installer.dmg"):
        os.remove("installer.dmg")
    print("Downloading the roblox installer")
    # --- code from google gemini lol (added osx user-agent cuz roblox keeps downloading the Windows version)
    response = requests.get(
        "https://www.roblox.com/download/client?os=mac",
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
        total=total_size, unit="B", unit_scale=True, desc="Downloading installer"
    )
    with open("installer.dmg", "wb") as file:
        for data in response.iter_content(1024):
            progress_bar.update(len(data))
            if not data:
                break
            file.write(data)
    progress_bar.close()
    # -------------------------------
    if not os.path.exists("installer.dmg"):
        print("Error while downloading the roblox dmg")
        return
    print("Attempting to mount the DMG")
    k = os.system("hdiutil mount installer.dmg")
    if k != 0:
        print(f"Error while mounting the DMG : {k}")
        return
    print("Mounted the DMG")
    # start thread
    print("Launching the installer")
    installer_process = Popen(
        "/Volumes/RobloxPlayerInstaller/RobloxPlayerInstaller.app/Contents/MacOS/RobloxPlayerInstaller"
    )
    completed = psutil.wait_procs([installer_process])
    if completed:
        print("Install completed successfully.")
    else:
        print("Installer timed out or failed.")
        installer_process.kill()
    KillRoblox()
    KillRobloxInstaller()
    print("Cleaning up")
    print("Unmounting the DMG")
    os.system("hdiutil detach /Volumes/RobloxPlayerInstaller")
    print("Deleting the DMG")
    os.remove("installer.dmg")
    KillRobloxInstaller()
    KillRoblox()


def GetRobloxVersion(plist_file):
    try:
        with open(plist_file, "rb") as fp:
            plist = plistlib.loads(fp.read())
            return plist["CFBundleShortVersionString"]
    except FileNotFoundError as e:
        return "Unknown"
    except Exception as e:
        print(f"Error getting roblox version : {e}")
        return "Unknown"


def GetLatestRobloxVersion():
    r = requests.get("https://clientsettings.roblox.com/v2/client-version/MacPlayer")
    if r.status_code != 200:
        print(f"Failed to get latest roblox : status_code : {r.status_code}")
        return "Unknown"
    k = r.json()
    return k["version"], k["clientVersionUpload"]


def get_versions(target_year, target_month):
    url = "https://setup.rbxcdn.com/mac/DeployHistory.txt"
    response = requests.get(url)

    if response.status_code == 200:
        content = response.text

        # Define regex pattern to extract version-hash and date
        pattern = r"New Client version-([a-f0-9]+) at (\d{1,2})/(\d{1,2})/(\d{4})"

        versions = []
        for line in content.split("\n"):
            match = re.search(pattern, line)
            if match:
                year, month = int(match.group(4)), int(match.group(2))
                if year == target_year and month == target_month:
                    version = f"version-{match.group(1)}"
                    date_published = (
                        f"{match.group(2)}/{match.group(3)}/{match.group(4)}"
                    )
                    versions.append((version, date_published))

        return versions

    else:
        print("Failed to fetch data")
        return None
