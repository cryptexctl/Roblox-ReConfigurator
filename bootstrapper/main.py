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
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any
from tqdm import tqdm
import mods

@dataclass
class BootstrapperConfig:
    do_not_update: bool = False
    channel: str = "Unknown"
    debug: bool = False
    show_output: bool = False
    reinstall: bool = False

class Bootstrapper:
    def __init__(self):
        self.paths = {
            'app': Path("/Applications/Roblox.app"),
            'player': Path("/Applications/Roblox.app/Contents/MacOS/RobloxPlayer"),
            'player_original': Path("/Applications/Roblox.app/Contents/MacOS/RobloxPlayer_original"),
            'mods': Path("mods"),
            'config': Path("bootstrapper.json")
        }
        self.config = self._load_config()
        self._setup_logging()
        self._setup_directories()

    def _load_config(self) -> BootstrapperConfig:
        config = BootstrapperConfig()
        
        for arg in sys.argv:
            if arg == "--no-update":
                config.do_not_update = True
            elif arg in ["-d", "--debug"]:
                config.debug = True
            elif arg in ["-s", "--show-output"]:
                config.show_output = True
            elif arg in ["-r", "--reinstall"]:
                config.reinstall = True
            elif arg in ["-h", "--help"]:
                self._show_help()
                sys.exit(0)
            elif arg == "--roblox-bootstrapper":
                self._launch_original_bootstrapper()
                sys.exit(0)

        if self.paths['config'].exists():
            try:
                with open(self.paths['config']) as f:
                    data = json.load(f)
                    config.do_not_update = data.get("do_not_update", False)
                    config.channel = data.get("channel", "Unknown")
            except Exception as e:
                logging.error(f"Failed to load config: {e}")

        return config

    def _setup_logging(self):
        level = logging.DEBUG if self.config.debug else logging.WARNING
        logging.basicConfig(
            level=level,
            format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )

    def _setup_directories(self):
        try:
            if not self.paths['config'].exists():
                self._save_config()
            
            if not self.paths['mods'].exists():
                self.paths['mods'].mkdir(parents=True)
        except Exception as e:
            logging.error(f"Failed to setup directories: {e}")

    def _save_config(self):
        try:
            with open(self.paths['config'], 'w') as f:
                json.dump({
                    "do_not_update": self.config.do_not_update,
                    "channel": self.config.channel
                }, f)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def _show_help(self):
        print("Roblox Configurator Bootstrapper")
        print("Made by Proton0")
        print("-h / --help            | Shows help command")
        print("-s / --show-output     | Shows roblox's output")
        print("--no-update           | Forces roblox configurator to not update roblox")
        print("--reinstall           | Will reinstall roblox (requires updates to be enabled)")
        print("-d                    | Enables debugging mode")
        print("--roblox-bootstrapper | Launches roblox's original bootstrapper")

    def _launch_original_bootstrapper(self):
        try:
            if not self.paths['player_original'].exists():
                logging.error("Original Roblox player not found")
                return

            subprocess.Popen(
                [str(self.paths['player_original'])],
                stdout=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            logging.error(f"Failed to launch original bootstrapper: {e}")

    def _notify(self, title: str, message: str):
        try:
            os.system(f"""
            osascript -e 'display notification "{message}" with title "{title}" sound name "Submarine"'
            """)
        except Exception as e:
            logging.error(f"Failed to show notification: {e}")

    def _download_file(self, url: str, filename: str) -> bool:
        try:
            response = requests.get(
                url=url,
                stream=True,
                allow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
                }
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            with tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading") as progress_bar:
                with open(filename, "wb") as file:
                    for data in response.iter_content(1024):
                        progress_bar.update(len(data))
                        file.write(data)
            return True
        except Exception as e:
            logging.error(f"Download failed: {e}")
            return False

    def _check_updates(self) -> bool:
        if self.config.do_not_update:
            logging.info("Skipping update due to configuration")
            return True

        try:
            if not self.paths['app'].exists():
                logging.error("Roblox is not installed")
                return False

            response = requests.get("https://clientsettings.roblox.com/v2/client-version/MacPlayer")
            response.raise_for_status()
            latest = response.json()

            with open(self.paths['app'] / "Contents/Info.plist", "rb") as fp:
                if self.config.reinstall:
                    current = {"CFBundleShortVersionString": "update"}
                else:
                    current = plistlib.loads(fp.read())

            if latest["version"] == current["CFBundleShortVersionString"]:
                logging.info("Roblox is up-to-date")
                return True

            logging.info("Downloading the latest version of Roblox")
            if not self._download_file(
                f"https://setup.rbxcdn.com/mac/{latest['clientVersionUpload']}-RobloxPlayer.zip",
                "Roblox.zip"
            ):
                return False

            with zipfile.ZipFile("Roblox.zip", "r") as zip_ref:
                zip_ref.extractall("client")

            shutil.move("client/RobloxPlayer.app", "Roblox.app")
            shutil.rmtree("client", ignore_errors=True)
            os.remove("Roblox.zip")
            
            logging.info("Roblox updated successfully")
            return True
        except Exception as e:
            logging.error(f"Update failed: {e}")
            return False

    def _install_mods(self):
        try:
            if not self.paths['mods'].exists():
                logging.warning("Mods directory not found")
                return

            for mod in self.paths['mods'].iterdir():
                if mod.is_dir():
                    logging.debug(f"Installing mod: {mod}")
                    mods.Install(str(mod), True)
        except Exception as e:
            logging.error(f"Mod installation failed: {e}")

    def _monitor_roblox(self):
        try:
            if not self.paths['player_original'].exists():
                logging.error("Original Roblox player not found")
                return

            process = subprocess.Popen(
                [str(self.paths['player_original'])],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            server_info = {
                'channel': "Unknown",
                'udmux_address': "Unknown",
                'udmux_port': "Unknown",
                'rcc_address': "Unknown",
                'rcc_port': "Unknown"
            }

            while True:
                line = process.stdout.readline().decode()
                if not line:
                    break

                if self.config.show_output:
                    logging.debug(line)

                # Extract channel
                if match := re.search(r"\[FLog::ClientRunInfo\] The channel is (.*)", line):
                    server_info['channel'] = match.group(1)
                    if self.config.channel != server_info['channel']:
                        old = self.config.channel
                        self.config.channel = server_info['channel']
                        self._save_config()
                        self._notify(
                            "Roblox Configurator",
                            f"Roblox has changed your channel from {old} to {server_info['channel']}!"
                        )

                # Extract server info
                if match := re.search(r"UDMUX Address = (\d+\.\d+\.\d+\.\d+), Port = (\d+)", line):
                    server_info['udmux_address'] = match.group(1)
                    server_info['udmux_port'] = match.group(2)

                if match := re.search(r"RCC Server Address = (\d+\.\d+\.\d+\.\d+), Port = (\d+)", line):
                    server_info['rcc_address'] = match.group(1)
                    server_info['rcc_port'] = match.group(2)

                if all(v != "Unknown" for v in server_info.values()):
                    self._show_server_info(server_info)
                    break

            # Continue monitoring output if show_output is enabled
            if self.config.show_output:
                while True:
                    line = process.stdout.readline().decode()
                    if not line:
                        break
                    print(line.strip())

        except Exception as e:
            logging.error(f"Failed to monitor Roblox: {e}")
            if self.config.debug:
                logging.error(traceback.format_exc())

    def _show_server_info(self, info: Dict[str, str]):
        try:
            response = requests.get(f"http://ip-api.com/json/{info['udmux_address']}")
            response.raise_for_status()
            data = response.json()

            if data["status"] == "success":
                message = (
                    f"Server: {data['country']}, {data['regionName']}, {data['city']}\n"
                    f"Server IP: {info['udmux_address']}\n"
                    f"Server Port: {info['udmux_port']}\n"
                    f"RCC IP: {info['rcc_address']}\n"
                    f"RCC Port: {info['rcc_port']}"
                )
                self._notify("Roblox Configurator", message)
            else:
                logging.error("Failed to get server data")
        except Exception as e:
            logging.error(f"Failed to get server info: {e}")

    def run(self):
        try:
            if not self.paths['app'].exists():
                logging.error("Roblox is not installed")
                return

            if not self._check_updates():
                return

            self._install_mods()
            self._monitor_roblox()
        except Exception as e:
            logging.error(f"Bootstrapper error: {e}")
            if self.config.debug:
                logging.error(traceback.format_exc())

if __name__ == "__main__":
    bootstrapper = Bootstrapper()
    bootstrapper.run()
