from pick import pick
import json
import shutil
import os


def CreateClientSettings():
    if not os.path.exists("/Applications/Roblox.app/Contents/MacOS/ClientSettings"):
        os.makedirs("/Applications/Roblox.app/Contents/MacOS/ClientSettings")
    if not os.path.exists(
        "/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json"
    ):
        file = open(
            "/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json",
            "w",
        )
        file.write("{}")
        file.close()


def WriteFFLag(name, value):
    CreateClientSettings()
    fflags_file = open(
        "/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json",
        "r",
    )
    fflags = json.loads(fflags_file.read())
    fflags_file.close()
    fflags_file = open(
        "/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json",
        "w",
    )
    fflags[name] = value
    fflags_file.write(json.dumps(fflags))
    fflags_file.close()


def DeleteFFLag(name):
    CreateClientSettings()
    print("Reading fflags")
    fflags_file = open(
        "/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json",
        "r",
    )
    print("Loading fflags")
    fflags = json.loads(fflags_file.read())
    fflags_file.close()
    fflags_file = open(
        "/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json",
        "w",
    )
    fflags.pop(name)
    fflags_file.write(json.dumps(fflags))
    fflags_file.close()


def FFlagLaunch():
    title = "Select an FFLag Tweak"
    options = [
        "Reset all FFLag tweaks",
        "Unlock FPS",
        "Enable 21 Graphics slider",
        "Configure lighting",
        "Configure textures",
        "Configure renderer",
        "Configure UI",
    ]
    option, index = pick(options, title)
    if option == "Reset all FFLag tweaks":
        shutil.rmtree(
            "/Applications/Roblox.app/Contents/MacOS/ClientSettings", ignore_errors=True
        )
        print("Succesfully deleted all FFLag tweaks")

    if option == "Unlock FPS":
        WriteFFLag("DFIntTaskSchedulerTargetFps", 144)
        print("Unlocked FPS succesfully")

    if option == "Unlock FPS + Enable Vulkan":
        WriteFFLag("DFIntTaskSchedulerTargetFps", 144)
        WriteFFLag("FFlagDebugGraphicsDisableMetal", True)
        WriteFFLag("FFlagDebugGraphicsPreferVulkan", True)
        print("Unlocked FPS and enabled vulkan succesfully")

    if option == "Enable 21 Graphics slider":
        WriteFFLag("FFlagFixGraphicsQuality", True)
        WriteFFLag("FFlagCommitToGraphicsQualityFix", True)
        print("Enabled 21 graphics slider")

    if option == "Configure lighting":
        Lights()

    if option == "Configure textures":
        Textures()

    if option == "Configure renderer":
        Render()

    if option == "Configure UI":
        UI()


def Lights():
    options = ["Enable Future", "Disable Future", "Enable Voxel", "Disable Voxel"]
    option, index = pick(options, "Select lighting config")
    if option == "Enable Future":
        WriteFFLag("FFlagDebugForceFutureIsBrightPhase3", True)
        print("Enabled Phase 3 lighting")

    if option == "Disable Future":
        WriteFFLag("FFlagDebugForceFutureIsBrightPhase3", False)
        print("Succesfully disabled Phase 3 lighting")

    if option == "Enable Voxel":
        WriteFFLag("DFFlagDebugRenderForceTechnologyVoxel", True)
        print("Enabled Phase 3 lighting")

    if option == "Disable Voxel":
        WriteFFLag("DFFlagDebugRenderForceTechnologyVoxel", False)
        print("Succesfully disabled Phase 3 lighting")


def Textures():
    options = ["Use old textures", "Use new textures"]
    option, index = pick(options, "Select textures")
    if option == "Use old textures":
        WriteFFLag("FStringPartTexturePackTable2022", False)
        WriteFFLag("FStringPartTexturePackTablePre2022", True)
        print("Forced roblox to use old textures")
    if option == "Use new textures":
        WriteFFLag("FStringPartTexturePackTable2022", True)
        WriteFFLag("FStringPartTexturePackTablePre2022", False)
        print("Forced roblox to use new textures")


def Render():
    options = ["Enable Vulkan", "Enable Metal", "Let roblox pick the renderer"]
    option, index = pick(options, "Select what renderer roblox will use")

    if option == "Let roblox pick the renderer":
        DeleteFFLag("FFlagDebugGraphicsPreferVulkan")  # delete prefer
        DeleteFFLag("FFlagDebugGraphicsPreferMetal")
        DeleteFFLag("FFlagDebugGraphicsPreferOpenGL")
        DeleteFFLag("FFlagDebugGraphicsDisableOpenGL")  # disable
        DeleteFFLag("FFlagDebugGraphicsDisableMetal")
        DeleteFFLag("FFlagDebugGraphicsDisableVulkan")
        print("Roblox will now pick the renderer")

    if option == "Enable Vulkan":
        WriteFFLag("FFlagDebugGraphicsPreferVulkan", True)
        # set prefer to false
        WriteFFLag("FFlagDebugGraphicsPreferMetal", False)
        WriteFFLag("FFlagDebugGraphicsPreferOpenGL", False)
        # disable others
        WriteFFLag("FFlagDebugGraphicsDisableOpenGL", True)
        WriteFFLag("FFlagDebugGraphicsDisableMetal", True)
        print("Vulkan will now be the renderer")
    if option == "Enable Metal":
        WriteFFLag("FFlagDebugGraphicsPreferMetal", True)
        # set prefer to false
        WriteFFLag("FFlagDebugGraphicsPreferVulkan", False)
        WriteFFLag("FFlagDebugGraphicsPreferOpenGL", False)
        # disable others
        WriteFFLag("FFlagDebugGraphicsDisableOpenGL", True)
        WriteFFLag("FFlagDebugGraphicsDisableVulkan", True)
        print("Metal will now be the renderer")
    if option == "Enable OpenGL":
        WriteFFLag("FFlagDebugGraphicsPreferOpenGL", True)
        # set prefer to false
        WriteFFLag("FFlagDebugGraphicsPreferVulkan", False)
        WriteFFLag("FFlagDebugGraphicsPreferMetal", False)
        # disable others
        WriteFFLag("FFlagDebugGraphicsDisableMetal", True)
        WriteFFLag("FFlagDebugGraphicsDisableVulkan", True)


def UI():
    options = [
        "V1",
        "V2 (default)",
        "V3",
    ]
    options, index = pick(options, "Select UI for roblox to use")

    if options == "V1":
        WriteFFLag("FFlagDisableNewIGMinDUA", False)
        WriteFFLag("FFlagEnableInGameMenuControls", False)
        WriteFFLag("FFlagEnableInGameMenuModernization", False)
        print("Enabled V1")

    if options == "V2 (default)":
        WriteFFLag("FFlagDisableNewIGMinDUA", True)
        WriteFFLag("FFlagEnableInGameMenuControls", True)
        WriteFFLag("FFlagEnableInGameMenuModernization", False)
        print("Enabled V2")

    if options == "V3":
        WriteFFLag("FFlagDisableNewIGMinDUA", True)
        WriteFFLag("FFlagEnableInGameMenuControls", False)
        WriteFFLag("FFlagEnableInGameMenuModernization", True)
        print("Enabled V3")
