"""
This module contains the OneDrive_API class which is used to interact with the OneDrive API.
"""
from datetime import datetime
from typing import Optional
import json
import os
import requests
import jwt
from msal import ConfidentialClientApplication

class OneDrive_API(object):
    """
    Class representing a OneDrive API service.
    """
    def __init__(self,client_id,client_secret,tenant_id,username_id,drive_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.username_id = username_id
        self.drive_id = drive_id
        self.app = ConfidentialClientApplication(
                        self.client_id,
                        self.client_secret,
                        authority=f"https://login.microsoftonline.com/{self.tenant_id}"
                        )
        self.token = self.app.acquire_token_for_client(
                        scopes=["https://graph.microsoft.com/.default"]
                        )
        self.access_token = self.token["access_token"]
        self.commonapi_point = "https://graph.microsoft.com/v1.0/"
        self.session = requests.Session()

    def check_token_expiration_time(self) -> None:
        """
        Check if the access token is about to expire and acquire a new one if necessary.

        Returns:
        None
        """

        # Decode the access token
        decoded_token = jwt.decode(
                            self.access_token,
                            options={"verify_signature": False}
                            )
        expiration_time = datetime.fromtimestamp(decoded_token['exp'])
        current_time = datetime.now()

        if (expiration_time - current_time).total_seconds() < 60:
            self.token = self.app.acquire_token_for_client(
                                scopes=["https://graph.microsoft.com/.default"]
                                )
            self.access_token = self.token["access_token"]
    def onedrive_header(self):
        """
        Create the headers for the OneDrive API.

        Returns:
        dict: The headers for the OneDrive API.
        """

        return{
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

    def read_onedrive_info(self,folderdir:str) -> dict:
        """
        Read the information of the files in the specified folder.

        Parameters:
        folderdir (str): The folder directory.

        Returns:
        dict: The information of the files in the folder.

        See Also:
        https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0&tabs=http
        """

        self.check_token_expiration_time()
        # API endpoint and headers
        if (self.drive_id != '' or self.drive_id is not None):
            #folderdir = 'Data Science:'
            api_endpoint = f"{self.commonapi_point}drives/{self.drive_id}/items/" \
                                f"root:/{folderdir}:/children"
        if (self.drive_id == '' or self.drive_id is None) and \
            (self.username_id is not None or self.username_id != ''):
            api_endpoint = f"{self.commonapi_point}users/{self.username_id}/" \
                                "drive/root/children"
        else:
            api_endpoint = None

        # Make the request
        response = self.session.get(
                        api_endpoint,
                        headers=self.onedrive_header(),
                        timeout=20
                        )

        # Process the response
        if response.status_code != 200:
            print(response.json())
            print('Request failed with status code:',
                    response.status_code)
        return response.json()

    def create_onedrive_folder(self,folderdir:str,newfoldername:str) -> dict:
        """
        Create a new folder in the specified directory.

        Parameters:
        folderdir (str): The folder directory.
        newfoldername (str): The name of the new folder.

        Returns:
        dict: The response from the API.
        """

        self.check_token_expiration_time()
        # Create file create link
        if (self.drive_id == '' or self.drive_id is None) and \
                (self.username_id is not None or self.username_id != ''):
            api_endpoint = f"{self.commonapi_point}users/{self.username_id}/" \
                                f"drive/root:/{folderdir}:/children"
        elif (self.drive_id != '' or self.drive_id is not None):
            api_endpoint = f"{self.commonapi_point}drives/{self.drive_id}/" \
                                f"items/root:/{folderdir}/children"
        else:
            api_endpoint = None

        payload = {
            "name": newfoldername,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }

        # Send the request to create the sharing link
        response = self.session.post(
                        api_endpoint,
                        headers=self.onedrive_header(),
                        data=json.dumps(payload),
                        timeout=20
                        )
        if response.status_code in [201,200]:
            print(f"File '{newfoldername}' uploaded successfully.")
        else:
            print(f"Failed to upload file '{newfoldername}'. \
                    Status code: {response.status_code}")
            print(response.json())

        return response.json()

    def upload_onedrive_file(self,file_path:str,filename:str,folderdir:str) -> dict:
        """
        Upload a file to the specified folder.

        Parameters:
        file_path (str): The path to the file to upload.
        filename (str): The name of the file.
        folderdir (str): The folder directory.

        Returns:
        dict: The response from the API.

        See Also:
        https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/driveitem_createuploadsession?view=odsp-graph-online
        https://dev.to/jsnmtr/automating-files-upload-to-microsoft-onedrive-unexpected-challenges-and-a-success-story-2ini
        https://github.com/jsnm-repo/Python-OneDriveAPI-FileUpload/blob/master/AutomatedOneDriveAPIUploadFiles-public.py
        """
        
        self.check_token_expiration_time()
        if (self.drive_id != '' or self.drive_id is not None):
            #folderdir = 'Data Science:'
            upload_url = f"{self.commonapi_point}drives/{self.drive_id}/items/root:/{folderdir}/{filename}"
        elif (self.drive_id == '' or self.drive_id is None) and \
            (self.username_id is not None or self.username_id != ''):
            upload_url = f"{self.commonapi_point}users/{self.username_id}/drive/root:/{folderdir}/{filename}"
        else:
            upload_url = None

        #file_path = os.path.join(root,file_name)
        file_size = os.stat(file_path).st_size
        if file_size < 4100000:
            with open(file_path, 'rb') as file_data:
                #Perform is simple upload to the API
                response = self.session.put(
                                upload_url+":/content",
                                data=file_data,
                                headers=self.onedrive_header()
                                )
                if response.status_code in [201,200]:
                    print(f"File '{filename}' uploaded successfully.")
                else:
                    print(f"Failed to upload file '{filename}'. \
                        Status code: {response.status_code}")
                    print(response.json())
                return response.json()
        else:
            upload_session = self.session.post(
                                    upload_url+":/createUploadSession",
                                    headers=self.onedrive_header()
                                ).json()
            with open(file_path, 'rb') as f:
                total_file_size = os.path.getsize(file_path)
                chunk_size = 327680
                chunk_number = total_file_size//chunk_size
                chunk_leftover = total_file_size - chunk_size * chunk_number
                i = 0
                while True:
                    chunk_data = f.read(chunk_size)
                    start_index = i*chunk_size
                    end_index = start_index + chunk_size
                    #If end of file, break
                    if not chunk_data:
                        break
                    if i == chunk_number:
                        end_index = start_index + chunk_leftover
                    #Setting the header with the appropriate chunk data location in the file
                    headers = {
                            'Content-Length': f'{chunk_size}',
                            'Content-Range': f'bytes {start_index}-{end_index - 1}/{total_file_size}'
                        }
                    #Upload one chunk at a time
                    response = self.session.put(
                                    upload_session['uploadUrl'],
                                    data=chunk_data,
                                    headers=headers
                                    )
                    i = i + 1
                    if response.status_code in [201,200,202]:
                        print(f"File '{filename}' uploaded successfully.")
                    else:
                        print(f"Failed to upload file '{filename}'. \
                            Status code: {response.status_code}")
        return response.json()

    def get_onedrive_sharelink(self, folderdir:str, filename: str) -> Optional[str]:
        """
        Get the sharing link for the specified file.

        Parameters:
        folderdir (str): The folder directory.
        filename (str): The name of the file.

        Returns:
        Optional[str]: The sharing link for the file.
        """

        self.check_token_expiration_time()
        # Create file create link
        if (self.drive_id != '' or self.drive_id is not None):
            #folderdir = 'Data Science:'
            upload_url = f"{self.commonapi_point}drives/{self.drive_id}" \
                            f"/items/root:/{folderdir}/" \
                            f"{filename}:/createLink"
        elif (self.drive_id == '' or self.drive_id is None) and \
            (self.username_id is not None or self.username_id != ''):
            upload_url = f"{self.commonapi_point}users/{self.username_id}" \
                            f"/drive/root:/{folderdir}/" \
                            f"{filename}:/createLink"
        else:
            upload_url = None

        request_body = {
                            "type": "edit",
                            "scope": "anonymous"
                        }

        # Send the request to create the sharing link
        response = self.session.post(
                        upload_url,
                        headers=self.onedrive_header(),
                        data=json.dumps(request_body)
                    )

        if response.status_code in [201,200]:
            return response.json()['link']['webUrl']
        else:
            print(f"Failed to upload file '{filename}'. \
                Status code: {response.status_code}")
            return None

    def close_onedrive_connection(self) -> None:
        """
        Close the connection to the OneDrive API.

        Returns:
        None
        """
        self.session.close()
