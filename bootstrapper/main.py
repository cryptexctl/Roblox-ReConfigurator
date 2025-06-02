import shutil
import sys
import os
import json
import re
import requests
import logging
import zipfile
import plistlib
import traceback
import mods
from tqdm import tqdm
import subprocess


def NotifyPlayer(title, message):
    os.system(
        f"""
    osascript -e 'display notification "{message}" with title "{title}" sound name "Submarine"'
    """
    )


def download(url, download):
    response = requests.get(
        url=url,
        stream=True,
        allow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
        },
    )
    if response.status_code != 200:
        logging.error(f"Error downloading file: {response.status_code}")
    else:
        total_size = int(response.headers.get("content-length", 0))
        progress_bar = tqdm(
            total=total_size, unit="B", unit_scale=True, desc="Downloading"
        )
        with open(download, "wb") as file:
            for data in response.iter_content(1024):
                progress_bar.update(len(data))
                if not data:
                    break
                file.write(data)
        progress_bar.close()

        if not os.path.exists(download):
            logging.error("Failed to download Roblox")


do_not_update = False
reinstall_roblox = False
debug = False
show_roblox_output = False
for argument in sys.argv:
    if argument == "--no-update":
        do_not_update = True
    if argument == "-d" or argument == "--debug":
        debug = True
    if argument == "-s" or argument == "--show-output":
        show_roblox_output = True
    if argument == "-r" or argument == "--reinstall":
        reinstall_roblox = True
    if argument == "-h" or argument == "--help":
        print("Roblox Configurator Bootstrapper")
        print("Made by Proton0")
        print("-h / --help            | Shows help command")
        print("-s / --show-output     | Shows roblox's output")
        print(
            "--no-update            | Forces roblox configurator to not update roblox"
        )
        print(
            "--reinstall            | Will reinstall roblox (requires updates to be enabled)"
        )
        print("-d                     | Enables debugging mode")
        print("--roblox-bootstrapper  | Launches roblox's original bootstrapper")
        exit()
    if argument == "--roblox-bootstrapper":
        subprocess.Popen(
            "/Applications/Roblox.app/Contents/MacOS/RobloxPlayer_original",
            stdout=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        exit()

if debug:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.info("debug mode is on")
else:
    logging.basicConfig(
        level=logging.WARNING,
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.info("debug mode is off")

if not os.path.exists("bootstrapper.json"):
    with open("bootstrapper.json", "w+") as f:
        f.write('{"do_not_update": false, "channel": "Unknown"}')
    print("Created configuration successfully")

if not os.path.exists("mods"):
    os.mkdir("mods")

bootstrapperConfiguration = json.load(open("bootstrapper.json"))
logging.info("loaded bootstrapper configuration succesfully")

if bootstrapperConfiguration["do_not_update"]:
    logging.info("Not updating Roblox")
    do_not_update = True

# Check for updates and delete the old bootstrapper
if os.path.exists("RobloxPlayerInstaller.app"):
    shutil.rmtree("RobloxPlayerInstaller.app")  # Delete the old bootstrapper

try:
    if not do_not_update:
        print("Checking for updates")
        r = requests.get(
            "https://clientsettings.roblox.com/v2/client-version/MacPlayer"
        )
        if r.status_code != 200:
            print(
                f"Failed to get the latest Roblox version. Status code: {r.status_code}"
            )
        else:
            k = r.json()
            with open("/Applications/Roblox.app/Contents/Info.plist", "rb") as fp:
                if reinstall_roblox:
                    plist = {"CFBundleShortVersionString": "update"}
                else:
                    plist = plistlib.loads(fp.read())
                if k["version"] == plist["CFBundleShortVersionString"]:
                    print("Roblox is up-to-date")
                else:
                    print("Downloading the latest version of Roblox")
                    download(
                        f"https://setup.rbxcdn.com/mac/{k['clientVersionUpload']}-RobloxPlayer.zip",
                        "Roblox.zip",
                    )
                    print("Successfully downloaded Roblox")
                    with zipfile.ZipFile("Roblox.zip", "r") as zip_ref:
                        zip_ref.extractall("client")
                    shutil.move("client/RobloxPlayer.app", "Roblox.app")
                    print("Roblox updated successfully")
                    print("Removing temp data")
                    shutil.rmtree("client", ignore_errors=True)
                    os.remove("Roblox.zip")
    else:
        logging.info("Skipping update due to terminal argument or configuration")
except Exception as e:
    logging.error(traceback.format_exc())
logging.info("testing...")
try:
    for mod in os.listdir("mods"):
        logging.debug(f"Adding {mod}")
        mods.Install("mods/" + mod, True)
except Exception as e:
    logging.error(e)

process = subprocess.Popen(
    ["/Applications/Roblox.app/Contents/MacOS/RobloxPlayer_original"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
channel_name = "Unknown"
udmux_address = "Unknown"
udmux_port = "Unknown"
rcc_server_address = "Unknown"
rcc_server_port = "Unknown"
found_udmux = False
found_rcc = False
server = None  # unknown
while process.stdout is None:
    print("Waiting for stdout...")

try:
    while True:
        line = process.stdout.readline().decode()
        if line:
            logging.debug(line)
            # Extract channel name using regular expressions (adapt if needed)
            match = re.search(r"\[FLog::ClientRunInfo\] The channel is (.*)", line)
            if match:
                logging.debug("Line matched with channel regex")
                channel_name = match.group(1)
                if bootstrapperConfiguration["channel"] != channel_name:
                    old = bootstrapperConfiguration["channel"]
                    bootstrapperConfiguration["channel"] = channel_name
                    logging.warning(
                        f"Roblox has changed your channel from {old} to {channel_name}!"
                    )
                    f = open("bootstrapper.json", "w")
                    f.write(json.dumps(bootstrapperConfiguration))
                    f.close()
                    NotifyPlayer(
                        "Roblox Configurator",
                        f"Roblox has changed your client's channel from {old} to {channel_name}!",
                    )
                break  # Exit the loop once the channel name is found
        else:
            logging.error("Failed to get channel")
            break
except Exception as e:
    logging.error(traceback.format_exc())
    if debug:
        process.kill()

try:
    while True:
        line = process.stdout.readline().decode()
        if line:
            logging.debug(line)
            match_udmux = re.search(
                r"UDMUX Address = (\d+\.\d+\.\d+\.\d+), Port = (\d+)", line
            )
            match_rcc = re.search(
                r"RCC Server Address = (\d+\.\d+\.\d+\.\d+), Port = (\d+)", line
            )
            if match_udmux:
                logging.info("matched with udmux details!")
                udmux_address = match_udmux.group(1)
                udmux_port = match_udmux.group(2)
                found_udmux = True
                logging.info("found udmux")
            if match_rcc:
                rcc_server_address = match_rcc.group(1)
                rcc_server_port = match_rcc.group(2)
                found_rcc = True
                logging.info("found rcc")

            # Exit the loop once both server details are found
            if found_udmux and found_rcc:
                server = requests.get(f"http://ip-api.com/json/{udmux_address}").json()
                if server["status"] == "success":
                    logging.debug(server)
                    NotifyPlayer(
                        "Roblox Configurator",
                        f"Server: {server['country']}, {server['regionName']}, {server['city']}\nServer IP: {udmux_address}\nServer Port: {udmux_port}\nRCC IP: {rcc_server_address}\nRCC Port: {rcc_server_port}",
                    )
                else:
                    logging.error("Failed to get server data")
                    NotifyPlayer(
                        "Roblox Configurator",
                        f"Failed to get server region\nServer IP: {udmux_address}\nServer Port: {udmux_port}\nRCC IP: {rcc_server_address}\nRCC Port: {rcc_server_port}",
                    )
                break  # Exit the loop once both server details are found
        else:
            logging.error("Invalid line detected (roblox has stopped)")
            break
except Exception as e:
    logging.error(traceback.format_exc())
    if debug:
        process.kill()

while process.poll() is None:
    if show_roblox_output:
        print(process.stdout.readline().decode())

logging.debug("roblox exited")
logging.debug("saving configuration (just in case)")
f = open("bootstrapper.json", "w")
f.write(json.dumps(bootstrapperConfiguration))
f.close()
logging.debug("write success")
exit(0)
