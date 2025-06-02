import logging
from pick import pick
import time
from patches import RobloxManager, RobloxInstaller
import backups
import getserver
import fflags
import mods

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MenuManager:
    def __init__(self):
        self.roblox = RobloxManager()
        self.installer = RobloxInstaller()

    def get_menu_title(self):
        try:
            version = self.roblox.get_version()
            if version == "Unknown":
                return "Roblox Configurator 2.1 for MacOS"
            return f"Roblox Configurator 2.1 for MacOS (Roblox: {version})"
        except Exception as e:
            logger.error(f"Failed to get menu title: {e}")
            return "Roblox Configurator 2.1 for MacOS"

    def get_menu_options(self):
        return [
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

    def handle_option(self, option):
        try:
            if option == "Install Bootstrapper (beta)":
                logger.warning("Bootstrapper is in beta and may cause issues")
                logger.warning("It is recommended to NOT launch roblox using the web browser!")
                if input("Press y to install: ").lower() == "y":
                    if self.installer.install_bootstrapper():
                        logger.info("Bootstrapper installed successfully")
                    else:
                        logger.error("Failed to install bootstrapper")
            elif option == "Backups":
                backups.BackupMain()
            elif option == "Mods":
                mods.InstallUI()
            elif option == "Uninstall Roblox":
                options = [
                    "Reset (will remove configs but not the app)",
                    "App uninstall (will uninstall player and studio)",
                ]
                title = "Select what type"
                option, _ = pick(options, title)
                if not self.roblox.uninstall(reset_only=(option == options[0])):
                    logger.error("Failed to uninstall Roblox")
            elif option == "Install Roblox Studio":
                if not self.installer.install_studio():
                    logger.error("Failed to install Roblox Studio")
            elif option == "Get roblox channel":
                getserver.GetRobloxChannel()
            elif option == "Launch roblox and get server ip and port":
                getserver.Launch()
            elif option == "Launch roblox":
                if not self.roblox.launch():
                    logger.error("Failed to launch Roblox")
            elif option == "Install Roblox":
                if not self.installer.install_player():
                    logger.error("Failed to install Roblox")
            elif option == "Get roblox version":
                latest_version, latest_hash = self.roblox.get_latest_version()
                current_version = self.roblox.get_version()
                logger.info(f"Installed: {current_version}")
                logger.info(f"Latest: {latest_version}")
                logger.info(f"Latest version hash: {latest_hash}")
                if latest_version == current_version:
                    logger.info("Client is up-to-date!")
            elif option == "FFLag Tweaks":
                fflags.FFlagLaunch()
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(60)

def main():
    menu = MenuManager()
    while True:
        try:
            option, _ = pick(menu.get_menu_options(), menu.get_menu_title())
            menu.handle_option(option)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Menu error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
