import os
import re
import shutil
import plistlib
import requests
import psutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RobloxPaths:
    APP: Path = Path("/Applications/Roblox.app")
    STUDIO: Path = Path("/Applications/RobloxStudio.app")
    LIBRARY: Path = Path.home() / "Library"
    PREFERENCES: Path = LIBRARY / "Preferences"
    LOGS: Path = LIBRARY / "Logs"
    CACHES: Path = LIBRARY / "Caches"
    SAVED_STATE: Path = LIBRARY / "Saved Application State"

class RobloxInstaller:
    def __init__(self):
        self.paths = RobloxPaths()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
        }

    def download_file(self, url: str, filename: str) -> bool:
        try:
            response = requests.get(url, stream=True, headers=self.headers)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            with tqdm(total=total_size, unit="B", unit_scale=True, desc=f"Downloading {filename}") as progress_bar:
                with open(filename, "wb") as file:
                    for data in response.iter_content(1024):
                        progress_bar.update(len(data))
                        file.write(data)
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False

    def mount_dmg(self, dmg_path: str) -> bool:
        try:
            result = os.system(f"hdiutil mount {dmg_path}")
            if result != 0:
                logger.error(f"Failed to mount DMG: {result}")
                return False
            return True
        except Exception as e:
            logger.error(f"Mount error: {e}")
            return False

    def unmount_dmg(self, volume_name: str) -> bool:
        try:
            os.system(f"hdiutil detach /Volumes/{volume_name}")
            return True
        except Exception as e:
            logger.error(f"Unmount error: {e}")
            return False

    def run_installer(self, installer_path: str) -> bool:
        try:
            installer_process = subprocess.Popen([installer_path])
            installer_process.wait()
            return installer_process.returncode == 0
        except Exception as e:
            logger.error(f"Installer error: {e}")
            return False

    def install_bootstrapper(self) -> bool:
        try:
            logger.info("Installing bootstrapper...")
            
            bootstrapper_path = self.paths.APP / "Contents/MacOS/bootstrapper"
            player_path = self.paths.APP / "Contents/MacOS/RobloxPlayer"
            player_original_path = self.paths.APP / "Contents/MacOS/RobloxPlayer_original"
            
            if not self.paths.APP.exists():
                logger.error("Roblox is not installed")
                return False

            if bootstrapper_path.exists():
                logger.info("Reinstalling the bootstrapper")
                shutil.rmtree(bootstrapper_path)
                if player_path.exists():
                    player_path.unlink()
                if player_original_path.exists():
                    player_original_path.rename(player_path)

            if not player_original_path.exists() and player_path.exists():
                player_path.rename(player_original_path)

            if not Path("bootstrapper").exists():
                logger.error("Bootstrapper files not found")
                return False

            # Копируем все файлы бутстраппера
            shutil.copytree("bootstrapper", bootstrapper_path)
            
            # Копируем скрипт запуска
            shutil.copyfile("bootstrapper/RobloxPlayer", player_path)
            
            # Устанавливаем права на выполнение
            os.system(f"chmod +x {bootstrapper_path}/main.py")
            os.system(f"chmod +x {bootstrapper_path}/RobloxPlayer")
            os.system(f"chmod +x {player_path}")
            
            # Удаляем старый установщик
            installer_path = self.paths.APP / "Contents/MacOS/RobloxPlayerInstaller.app"
            if installer_path.exists():
                shutil.rmtree(installer_path, ignore_errors=True)
            
            logger.info("Bootstrapper installed successfully")
            return True
        except Exception as e:
            logger.error(f"Bootstrapper installation failed: {e}")
            return False

    def install_player(self) -> bool:
        try:
            if self.paths.APP.exists():
                logger.info("Reinstalling Roblox")
                shutil.rmtree(self.paths.APP)

            if not self.download_file("https://www.roblox.com/download/client?os=mac", "installer.dmg"):
                return False

            if not self.mount_dmg("installer.dmg"):
                return False

            success = self.run_installer("/Volumes/RobloxPlayerInstaller/RobloxPlayerInstaller.app/Contents/MacOS/RobloxPlayerInstaller")
            
            self.cleanup_processes()
            self.unmount_dmg("RobloxPlayerInstaller")
            os.remove("installer.dmg")
            
            return success
        except Exception as e:
            logger.error(f"Player installation failed: {e}")
            return False

    def install_studio(self) -> bool:
        try:
            if self.paths.STUDIO.exists():
                logger.info("Reinstalling Roblox Studio")
                shutil.rmtree(self.paths.STUDIO)

            if not self.download_file("https://setup.rbxcdn.com/mac/RobloxStudio.dmg", "installer.dmg"):
                return False

            if not self.mount_dmg("installer.dmg"):
                return False

            success = self.run_installer("/Volumes/RobloxStudioInstaller/RobloxStudioInstaller.app/Contents/MacOS/RobloxStudioInstaller")
            
            self.unmount_dmg("RobloxStudioInstaller")
            os.remove("installer.dmg")
            
            return success
        except Exception as e:
            logger.error(f"Studio installation failed: {e}")
            return False

    def cleanup_processes(self):
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in ['Roblox', 'RobloxPlayerInstaller_patched']:
                    try:
                        proc.kill()
                    except:
                        pass
        except Exception as e:
            logger.error(f"Process cleanup failed: {e}")

class RobloxManager:
    def __init__(self):
        self.paths = RobloxPaths()
        self.installer = RobloxInstaller()

    def launch(self) -> bool:
        try:
            player_path = self.paths.APP / "Contents/MacOS/RobloxPlayer"
            player_original_path = self.paths.APP / "Contents/MacOS/RobloxPlayer_original"
            
            if not player_path.exists():
                logger.error("Roblox is not installed")
                return False

            if not player_original_path.exists():
                logger.error("Original Roblox player not found")
                return False

            subprocess.Popen([str(player_path)])
            return True
        except Exception as e:
            logger.error(f"Launch failed: {e}")
            return False

    def uninstall(self, reset_only: bool = False) -> bool:
        try:
            if reset_only:
                logger.info("Resetting Roblox configuration")
                self._reset_config()
            else:
                logger.info("Uninstalling Roblox completely")
                shutil.rmtree(self.paths.APP, ignore_errors=True)
                shutil.rmtree(self.paths.STUDIO, ignore_errors=True)
            return True
        except Exception as e:
            logger.error(f"Uninstall error: {e}")
            return False

    def _reset_config(self):
        try:
            paths_to_remove = [
                self.paths.APP / "Contents/MacOS/ClientSettings",
                self.paths.LIBRARY / "Roblox",
                self.paths.LOGS / "Roblox",
                self.paths.SAVED_STATE / "com.Roblox.RobloxStudio.savedState",
                self.paths.CACHES / "com.Roblox.StudioBootstrapper"
            ]
            
            for path in paths_to_remove:
                shutil.rmtree(path, ignore_errors=True)

            prefs_to_remove = [
                "com.Roblox.Roblox.plist",
                "com.roblox.RobloxPlayerChannel.plist",
                "com.roblox.RobloxPlayer.plist",
                "com.roblox.RobloxStudio.plist",
                "com.roblox.RobloxStudioChannel.plist"
            ]
            
            for pref in prefs_to_remove:
                try:
                    os.remove(self.paths.PREFERENCES / pref)
                except:
                    pass
        except Exception as e:
            logger.error(f"Config reset failed: {e}")

    def get_version(self) -> str:
        try:
            with open(self.paths.APP / "Contents/Info.plist", "rb") as fp:
                plist = plistlib.loads(fp.read())
                return plist["CFBundleShortVersionString"]
        except Exception as e:
            logger.error(f"Version check error: {e}")
            return "Unknown"

    def get_latest_version(self) -> Tuple[str, str]:
        try:
            response = requests.get("https://clientsettings.roblox.com/v2/client-version/MacPlayer")
            response.raise_for_status()
            data = response.json()
            return data["version"], data["clientVersionUpload"]
        except Exception as e:
            logger.error(f"Latest version check error: {e}")
            return "Unknown", "Unknown"

    def get_historical_versions(self, target_year: int, target_month: int) -> Optional[List[Tuple[str, str]]]:
        try:
            response = requests.get("https://setup.rbxcdn.com/mac/DeployHistory.txt")
            response.raise_for_status()
            
            pattern = r"New Client version-([a-f0-9]+) at (\d{1,2})/(\d{1,2})/(\d{4})"
            versions = []
            
            for line in response.text.split("\n"):
                if match := re.search(pattern, line):
                    year, month = int(match.group(4)), int(match.group(2))
                    if year == target_year and month == target_month:
                        version = f"version-{match.group(1)}"
                        date = f"{match.group(2)}/{match.group(3)}/{match.group(4)}"
                        versions.append((version, date))
            
            return versions
        except Exception as e:
            logger.error(f"Historical versions check error: {e}")
            return None
