from colorama import Fore
import os
from dotenv import load_dotenv

load_dotenv()

def logo():
    print(Fore.RED + r"""
  ________.__                    __  .__          ________            ___.  ___.
 /  _____/|  |__   ____  _______/  |_|  | ___.__./  _____/___________ \_ |__\_ |__   ___________
/   \  ___|  |  \ /  _ \/  ___/\   __\  |<   |  /   \  __\_  __ \__  \ | __ \| __ \_/ __ \_  __ \
\    \_\  \   Y  (  <_> )___ \  |  | |  |_\___  \    \_\  \  | \// __ \| \_\ \ \_\ \  ___/|  | \/
 \______  /___|  /\____/____  > |__| |____/ ____|\______  /__|  (____  /___  /___  /\___  >__|
        \/     \/           \/            \/            \/           \/    \/    \/     \/
""" + Fore.BLUE + """
                             Created by Nighty3098
""")
    
def get_user_data() -> tuple[str, str, str, str, bool]:
    """
    Ask user for the folder path and channel name. API_ID and API_HASH are read from environment variables.
    Returns:
        (API_ID, API_HASH, CHANNEL_NAME, PATH, session_exists)
    """
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    if not API_ID or not API_HASH:
        raise RuntimeError("API_ID and API_HASH must be set in your environment or .env file.")
    PATH = os.path.expanduser(input("ENTER THE PATH TO THE FOLDER WHERE ALL THE DATA WILL BE SAVED\n-> "))
    session_path = os.path.join(PATH, "anon_session.session")
    session_exists = os.path.exists(session_path)
    CHANNEL_NAME = input("ENTER CHANNEL NAME (without @)\n-> ")
    return API_ID, API_HASH, CHANNEL_NAME, PATH, session_exists
