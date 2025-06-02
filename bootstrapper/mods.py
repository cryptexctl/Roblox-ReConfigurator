import os
import shutil
import logging
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)

def Install(mod_path: str, silent: bool = False) -> bool:
    try:
        if not silent:
            print("Please do not launch roblox!")

        mod_path = Path(mod_path)
        if not mod_path.exists():
            logger.error(f"Mod not found: {mod_path}")
            return False

        app_path = Path("/Applications/Roblox.app")
        if not app_path.exists():
            logger.error("Roblox is not installed")
            return False

        content_path = app_path / "Contents/MacOS/ClientSettings"
        if not content_path.exists():
            content_path.mkdir(parents=True)

        for item in mod_path.iterdir():
            if item.is_file():
                target = content_path / item.name
                if target.exists():
                    target.unlink()
                shutil.copy2(item, target)
                logger.info(f"Replacing content: {item.name}")
            elif item.is_dir():
                target = content_path / item.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
                logger.info(f"Replacing ExtraContent: {item.name}")

        logger.info("Mod installed successfully")
        return True
    except Exception as e:
        logger.error(f"Mod installation failed: {e}")
        return False
