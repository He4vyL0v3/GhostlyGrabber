from colorama import Back, Fore, Style, init


def logo():
    print(
        Fore.RED
        + "  _____ _               _   _        _____           _     _               "
    )
    print(
        Fore.RED
        + " / ____| |             | | | |      / ____|         | |   | |              "
    )
    print(
        Fore.RED
        + "| |  __| |__   ___  ___| |_| |_   _| |  __ _ __ __ _| |__ | |__   ___ _ __ "
    )
    print(
        Fore.RED
        + "| | |_ | '_ \\ / _ \\/ __| __| | | | | | |_ | '__/ _` | '_ \\| '_ \\ / _ \\ '__|"
    )
    print(
        Fore.RED
        + "| |__| | | | | (_) \\__ \\ |_| | |_| | |__| | | | (_| | |_) | |_) |  __/ |   "
    )
    print(
        Fore.RED
        + " \\_____|_| |_|\\___/|___/\\__|_|\\__, |\\_____|_|  \\__,_|_.__/|_.__/ \\___|_|   "
    )
    print(
        Fore.RED
        + "                                __/ |                                      "
    )
    print(
        Fore.RED
        + "                               |___/                                       "
    )
    print(
        Fore.BLUE
        + "                                                                           "
    )
    print(
        Fore.BLUE
        + "                         Created by Nighty3098                             "
    )
    print(
        Fore.BLUE
        + "                                                                           "
    )


def get_user_data() -> tuple[str, str, str, str]:
    API_ID = input("ENTER YOUR API_ID\n->")
    API_HASH = input("ENTER YOUR API_HASH\n->")
    CHANNEL_NAME = input("ENTER CHANNEL NAME (without @)\n->")
    PATH = input("ENTER THE PATH TO THE FOLDER WHERE ALL THE DATA WILL BE SAVED\n->")

    return API_ID, API_HASH, CHANNEL_NAME, PATH
