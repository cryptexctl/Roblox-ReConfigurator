import shutil
import subprocess

from pick import pick

import backups
import os
import getserver
import fflags

import mods
import patches
import time

while True:
    version_roblox = patches.GetRobloxVersion(
        "/Applications/Roblox.app/Contents/Info.plist"
    )
    if version_roblox == "Unknown":
        title = "Roblox Configurator 2.1 for MacOS"
    else:
        title = f"Roblox Configurator 2.1 for MacOS (Roblox: {version_roblox})"
    options = [
        "Install Roblox",
        "Install Roblox Studio",
        "Uninstall Roblox",
        "FFLag Tweaks",
        "Get roblox version",
        "Launch roblox",
        "Launch roblox and get server ip and port",
        "Get roblox channel",
        "Mods",
        "Backups",
        "Install Bootstrapper (beta)",
    ]

    option, index = pick(options, title)
    try:

        if option == "Install Bootstrapper (beta)":
            print("WARN: The bootstrapper is in beta and may cause some issues")
            print("It is recommended to NOT launch roblox using the web broswer!")
            if input("Press y to install : ").lower() == "y":
                print("Installing. Please wait!")
                if os.path.exists(
                    "/Applications/Roblox.app/Contents/MacOS/bootstrapper"
                ):
                    print("Reinstalling the bootstrapper")
                    shutil.rmtree(
                        "/Applications/Roblox.app/Contents/MacOS/bootstrapper"
                    )
                    os.remove("/Applications/Roblox.app/Contents/MacOS/RobloxPlayer")
                    os.rename(
                        "/Applications/Roblox.app/Contents/MacOS/RobloxPlayer_original",
                        "/Applications/Roblox.app/Contents/MacOS/RobloxPlayer",
                    )
                if not os.path.exists(
                    "/Applications/Roblox.app/Contents/MacOS/RobloxPlayer_original"
                ):
                    os.rename(
                        "/Applications/Roblox.app/Contents/MacOS/RobloxPlayer",
                        "/Applications/Roblox.app/Contents/MacOS/RobloxPlayer_original",
                    )
                shutil.copytree(
                    "bootstrapper",
                    "/Applications/Roblox.app/Contents/MacOS/bootstrapper",
                )
                shutil.copyfile(
                    "bootstrapper/RobloxPlayer",
                    "/Applications/Roblox.app/Contents/MacOS/RobloxPlayer",
                )
                os.system(
                    "chmod +x /Applications/Roblox.app/Contents/MacOS/RobloxPlayer"
                )
                shutil.rmtree(
                    "/Applications/Roblox.app/Contents/MacOS/RobloxPlayerInstaller.app",
                    ignore_errors=True,
                )

        if option == "Backups":
            backups.BackupMain()
        if option == "Mods":
            mods.InstallUI()
        if option == "Uninstall Roblox":
            patches.UninstallRoblox()
        if option == "Install Roblox Studio":
            patches.install_studio()
        if option == "Get roblox channel":
            getserver.GetRobloxChannel()
        if option == "Launch roblox and get server ip and port":
            getserver.Launch()
        if option == "Launch roblox":
            subprocess.run(["/Applications/Roblox.app/Contents/MacOS/RobloxPlayer"])
        if option == "Install Roblox":
            patches.install()

        if option == "Get roblox version":
            k, b = patches.GetLatestRobloxVersion()
            print(
                f'Installed: {patches.GetRobloxVersion("/Applications/Roblox.app/Contents/Info.plist")}'
            )
            print(f"Latest : {k}")
            print(f"Latest version hash : {b}")
            if k == patches.GetRobloxVersion(
                "/Applications/Roblox.app/Contents/Info.plist"
            ):
                print("Client is up-to-date!")

        if option == "FFLag Tweaks":
            fflags.FFlagLaunch()
        time.sleep(5)
    except Exception as e:
        print(f"Error : {e}")
        time.sleep(60)
