
import requests
import os
import json
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv
import time


# Load configuration variables from .env
load_dotenv()

hubId = os.environ["HUB_ID"]
projectId = os.environ["PROJECT_ID"]
parentFolderUrn = os.environ["PARENT_FOLDER_URN"]

# Method ot send a request to the API
def send_request(url, headers=None, data=None, method='GET'):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        resp = resp = requests.request(method, url, data=data, headers=headers)
        if resp.status_code == 429:  # Too Many Requests
            retry_after = int(resp.headers.get("Retry-After", 3))  # Default to 1 second if not provided
            print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
            retries += 1
        else:
            resp.raise_for_status()  # Raise an exception for other HTTP errors
            return resp.json()

    raise Exception(f"Request failed after {max_retries} retries due to rate limiting.")

def select_folder():
    """
    Open a dialog for the user to select a folder.

    Returns:
        str: The path to the selected folder, or None if no folder was selected.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    folder_path = filedialog.askdirectory(title="Select a Folder")
    return folder_path

def get_access_token():
    token_response = send_request(
        "https://developer.api.autodesk.com/authentication/v2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_id": os.environ["AUTODESK_CLIENT_ID"],
            "client_secret": os.environ["AUTODESK_CLIENT_SECRET"],
            "grant_type": "client_credentials",
            "scope": "data:read data:write data:create account:read"
        },
        method='POST'
    )
    access_token = token_response["access_token"]
    return access_token

def get_folder(projectId, folderId, access_token):
    # Get the folder details from the API.
    folder_details = send_request(
        f"https://developer.api.autodesk.com/data/v1/projects/{projectId}/folders/{folderId}",
        headers={"Authorization": "Bearer "+ access_token}
    )
    return folder_details

def get_user_id(access_token, hubId):
    # Get the user ID from the API.
    user_details = send_request(
        f"https://developer.api.autodesk.com/hq/v1/accounts/{hubId}/users/search?email={os.environ['USER_EMAIL']}",
        headers={"Authorization": "Bearer "+ access_token}
    )
    user_id = user_details[0]["uid"]
    return user_id

def create_folder(projectId, parentFolderUrn, folderName, access_token, user_id):
    # Create a new folder in the specified project and parent folder.
    payload = {
        "jsonapi": {
          "version": "1.0"
        },
        "data": {
          "type": "folders",
          "attributes": {
            "name": folderName,
            "extension": {
              "type": "folders:autodesk.bim360:Folder",
              "version": "1.0"
            }
          },
          "relationships": {
            "parent": {
              "data": {
                "type": "folders",
                "id": parentFolderUrn
              }
            }
          }
        }
      }
    created_folder = send_request(
        f"https://developer.api.autodesk.com/data/v1/projects/{projectId}/folders",
        headers={"Authorization": "Bearer "+ access_token, "x-user-id":user_id},
        data=json.dumps(payload),
        method='POST'
    )
    return created_folder

def traverse_folder_structure(root_folder, parentFolderUrn, user_id):
    """
    Traverse the folder structure starting from the root folder.

    Args:
        root_folder (str): The path to the root folder.

    Returns:
        list: A list of dictionaries representing the folder structure recursively.
    """
    def traverse(folder_path, parentFolderUrn, user_id):
        """
        Helper function to recursively traverse a folder.

        Args:
            folder_path (str): The path to the folder.

        Returns:
            dict: A dictionary representing the folder and its children.
        """
        folder_data = {
            "name": os.path.basename(folder_path),
            "path": os.path.relpath(folder_path, root_folder),
            "subfolders": [],
            "folderURN": None
        }
        new_folder = create_folder(projectId, parentFolderUrn, folder_data["name"], access_token, user_id)
        folder_data["folderURN"] = new_folder["data"]["id"]

        for entry in os.scandir(folder_path):
            if entry.is_dir():
                folder_data["subfolders"].append(traverse(entry.path, folder_data["folderURN"], user_id))

        return folder_data

    return traverse(root_folder, parentFolderUrn, user_id)

access_token = get_access_token()

user_id = get_user_id(access_token, hubId)

# Select a local folder
local_folder = select_folder()

folder_structure = traverse_folder_structure(local_folder, parentFolderUrn, user_id)

print("process done!")