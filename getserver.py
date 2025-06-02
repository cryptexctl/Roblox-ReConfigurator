import os
import subprocess
import time
import re
import requests
import psutil


def NotifyPlayer(title, message):
    os.system(
        f"""
    osascript -e 'display notification "{message}" with title "{title}" sound name "Submarine"'
    """
    )


def Launch(process=None):
    NotifyPlayer("Roblox Configurator", "Please launch a game")
    hasFound = False
    if process is None:
        process = subprocess.Popen(
            ["/Applications/Roblox.app/Contents/MacOS/RobloxPlayer"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    found_udmux = False
    found_rcc = False
    while True:
        line = process.stdout.readline().decode()
        if line:
            print(line)
            match = re.search(
                r"UDMUX Address = (\d+\.\d+\.\d+\.\d+), Port = (\d+)", line
            )
            if match:
                udmux_address = match.group(1)
                udmux_port = match.group(2)
                found_udmux = True
                print("found udmux")

            match = re.search(
                r"RCC Server Address = (\d+\.\d+\.\d+\.\d+), Port = (\d+)", line
            )
            if match:
                rcc_server_address = match.group(1)
                rcc_server_port = match.group(2)
                found_rcc = True
                print("found rcc")

            # check
            if found_udmux and found_rcc:
                print("found")
                NotifyPlayer(
                    "Roblox Configurator",
                    f"Found server details\nServer IP : {udmux_address}\nServer Port : {udmux_port}\nRCC IP : {rcc_server_address}\nRCC Port : {rcc_server_port}",
                )
                print(f"Server IP : {udmux_address}")
                print(f"Server Port : {udmux_port}")
                print(f"RCC IP : {rcc_server_address}")
                print(f"RCC Port : {rcc_server_port}")
                print("Getting the information about the servers (may take a while)")
                server = requests.get(f"http://ip-api.com/json/{udmux_address}").json()
                if server["status"] == "success":
                    print(server)
                    NotifyPlayer(
                        "Roblox Configurator",
                        f"Got location of server!\nCountry: {server['country']}\nRegion: {server['regionName']}\nCity: {server['city']}\nTimezone: {server['timezone']}\nLAT: {server['lat']}\n LON: {server['lon']}\nISP: {server['isp']}",
                    )
                else:
                    print("Failed to get server data")
                break

        else:
            print("No more log output")
            if not hasFound:
                NotifyPlayer(
                    "Roblox Configurator",
                    "Failed to get server information\nReason: No more log output",
                )
                if found_rcc and found_udmux:
                    hasFound = True
                    break
                if found_udmux:
                    NotifyPlayer(
                        "Roblox Configurator",
                        f"Failed to get RCC\n Server IP : {udmux_address}\nServer Port : {udmux_port}",
                    )
                if found_rcc:
                    NotifyPlayer(
                        "Roblox Configurator",
                        f"Failed to get Server\nRCC IP : {rcc_server_address}\nRCC Port: {rcc_server_port}",
                    )
            time.sleep(5)
            break


def GetRobloxChannel():
    NotifyPlayer("Roblox Configurator", "Please join a game!")
    hasFound = False
    channel_name = "Unknown"
    process = subprocess.Popen(
        ["/Applications/Roblox.app/Contents/MacOS/RobloxPlayer"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print("Getting the channel. Please wait!")
    while not hasFound:
        line = process.stdout.readline().decode()
        if line:
            # Extract channel name using regular expressions (adapt if needed)
            match = re.search(r"\[FLog::ClientRunInfo\] The channel is (.*)", line)
            if match:
                channel_name = match.group(1)
                hasFound = True
        else:
            if not hasFound:
                print("Failed to get channel")
            return
    process.kill()
    NotifyPlayer("Roblox Configurator", f"Client channel is {channel_name}")
    print(f"Client channel is {channel_name}")
