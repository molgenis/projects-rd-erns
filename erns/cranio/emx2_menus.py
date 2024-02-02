"""Create new menus"""

import random
import string


def generate_key(size=6):
    """Generate a random string
    :param size: length of the random string
    :type size: int

    :return random string of letters and numbers
    """
    choices = string.ascii_letters + string.digits
    result = random.choices(choices, k=size)
    return ''.join(result)


def new_public_menu():
    """Create a new json object for the public menu"""
    menu = [
        {
            "label": "Home",
            "href": "./cranio-public",
            "role": "Viewer"
        },
        {
            "label": "Tables",
            "href": "tables",
            "role": "Viewer"
        },
        {
            "label": "Schema",
            "href": "schema",
            "role": "Manager"
        },
        {
            "label": "Up/Download",
            "href": "updownload",
            "role": "Editor"
        },
        {
            "label": "Graphql",
            "href": "graphql-playground",
            "role": "Editor"
        },
        {
            "label": "Settings",
            "href": "settings",
            "role": "Manager"
        },
        {
            "label": "Help",
            "href": "docs",
            "role": "Viewer"
        }
    ]

    set_menu_keys(menu)
    return menu


def new_provider_menu():
    """Create a new json object for the provider menu"""
    menu = [
        {
            "label": "Home",
            "href": "./cranio-provider",
            "role": "Viewer"
        },
        {
            "label": "Patients",
            "href": "tables/#/Subject",
            "role": "Editor"
        },
        {
            "label": "Visit per workstream",
            "href": "",
            "submenu": [
                {
                    "label": "CRANIOSYNOSTOSIS workstream",
                    "href": "tables/#/Visits_synostosis",
                    "role": "Editor"
                },
                {
                    "label": "CLEFT workstream",
                    "href": "tables/#/Visits_cleft",
                    "role": "Editor"
                }
            ],
            "role": "Editor"
        },
        {
            "label": "Tables",
            "href": "tables",
            "role": "Viewer"
        },
        {
            "label": "Schema",
            "href": "schema",
            "role": "Manager"
        },
        {
            "label": "Up/Download",
            "href": "updownload",
            "role": "Editor"
        },
        {
            "label": "Graphql",
            "href": "graphql-playground",
            "role": "Viewer"
        },
        {
            "label": "Settings",
            "href": "settings",
            "role": "Manager"
        },
        {
            "label": "Help",
            "href": "docs",
            "role": "Viewer"
        }
    ]

    set_menu_keys(menu)
    return menu


def set_menu_keys(menu: list = None):
    """Set keys for all menu items"""
    for item in menu:
        item['key'] = generate_key()
        if 'submenu' in item.keys():
            set_menu_keys(menu=item['submenu'])


if __name__ == '__main__':
    k = generate_key(size=16)
    test_public = new_public_menu()
    test_provider = new_provider_menu()
