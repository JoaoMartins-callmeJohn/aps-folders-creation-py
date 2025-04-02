# aps-folders-creation-py
Quick acc folders creation tool

This Python script automates the creation of folders in Autodesk BIM 360 using the Autodesk Platform Services (APS) API. It traverses a local folder structure and replicates it in a BIM 360 project.

## Features
- **Folder Traversal**: Recursively traverses a local folder structure.
- **Folder Creation**: Creates corresponding folders in a BIM 360 project.
- **Rate Limiting Handling**: Automatically retries API requests when rate limits are exceeded (HTTP 429).
- **User-Friendly Folder Selection**: Allows users to select a local folder using a graphical interface.

---

## Prerequisites
1. **Python**: Ensure Python 3.7 or higher is installed.
2. **Dependencies**: Install the required Python libraries:
   ```bash
   pip install requests python-dotenv tkinter

3. Autodesk Platform Services (APS) Credentials:

Obtain your client_id and client_secret from the Autodesk Developer Portal.
Ensure you have access to the BIM 360 project and the necessary permissions to create folders.
Environment Variables: Create a .env file in the project directory with the following variables:

4. Environment Variables: Create a .env file in the project directory with the following variables:

HUB_ID=your_hub_id
PROJECT_ID=your_project_id
PARENT_FOLDER_URN=your_parent_folder_urn
AUTODESK_CLIENT_ID=your_client_id
AUTODESK_CLIENT_SECRET=your_client_secret
USER_EMAIL=your_email_address