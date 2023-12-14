import os
import google.auth
import google_auth_oauthlib.flow
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

class YouTubeUploader:
		def __init__(self):
				self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
				self.api_service_name = "youtube"
				self.api_version = "v3"
				self.credentials = None
				self.youtube = None
				
		def authenticate(self):
				# Load credentials if they exist
				if os.path.exists('token.json'):
						self.credentials = Credentials.from_authorized_user_file('token.json', self.scopes)

				# If there are no (valid) credentials available, let the user log in.
				if not self.credentials or not self.credentials.valid:
						if self.credentials and self.credentials.expired and self.credentials.refresh_token:
								self.credentials.refresh(google.auth.transport.requests.Request())
						else:
								flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
										'client_secrets.json', self.scopes)
								self.credentials = flow.run_local_server(port=0)
						# Save the credentials for the next run
						with open('token.json', 'w') as token:
								token.write(self.credentials.to_json())

				self.youtube = build(self.api_service_name, self.api_version, credentials=self.credentials, developerKey='AIzaSyDEojGLdiZKUZNFmedlzO9EuADdk1IfDxI')
		
		def upload_video(self, video_path, title, description, tags):
				# Get the video file size
				file_size = os.path.getsize(video_path)
				
				request_body = {
						'snippet': {
								'title': title,
								'description': description,
								'tags': tags,
								'categoryId': '22',
								'channelId': 'UCfLEK77pxb71q2aBKYyiOKw'
						},
						'status': {
								'privacyStatus': 'public',
								'notifySubscribers': True,
								'selfDeclaredMadeForKids': False
						},
				}

				# Call the API's videos.insert method to upload the video.
				try:
						# Create a video resource and set its metadata
						insert_request = self.youtube.videos().insert(
								part=",".join(request_body.keys()),
								body=request_body,
								media_body=MediaFileUpload(video_path)
						)
						response = insert_request.execute()

						print(f'Video id "{response["id"]}" was successfully uploaded.')
						print(response)
				except HttpError as e:
						print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
						
		def set_video_metadata(self, video_id, title, description, tags):
				request_body = {
						'id': video_id,
						'snippet': {
								'title': title,
								'description': description,
								'tags': tags
						}
				}
				
				# Call the API's videos.update method to set the video's metadata.
				try:
						update_request = self.youtube.videos().update(
								part=",".join(request_body.keys()),
								body=request_body
						)
						response = update_request.execute()
						
						print(f'Metadata for video id "{response["id"]}" was successfully updated.')
				except HttpError as e:
						print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))