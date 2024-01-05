from pathlib import Path
import sys
import os

# set both to True for the GitLan pipeline to run successfully
DEVELOPMENT = True  # Set to True for development, False for production
TESTING = True

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in a PyInstaller bundle
    app_base_path = Path(sys._MEIPASS) / 'data'
    data_base_path = Path(os.environ['LOCALAPPDATA']) / 'LearnoDoro'
else:
    # Running in a normal Python environment
    app_base_path = Path(__file__).parent / 'data'
    data_base_path = Path(__file__).parent / 'data' if DEVELOPMENT else Path(os.environ['LOCALAPPDATA']) / 'LearnoDoro'


if TESTING: data_base_path = Path(__file__).parent.parent / 'Tests'

data_base_path.mkdir(parents=True, exist_ok=True)

# Paths for database and settings (in local app data directory)
db_path = data_base_path / 'LearnoDoroApp.db'
settings_path = data_base_path / 'settings.json'

# Paths for sound and icon (relative to the application directory)
sound_path = app_base_path / 'mixkit-achievement-bell-600.wav'
icon_path = app_base_path / 'LearnoDoroLogo1.ico'
