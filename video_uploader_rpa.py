import os
from youtube_auto_upload import YouTubeUploader
from youtube_auto_login import YoutubeLogin

class YoutubeUploaderRPA():
  def __init__(self, channel, driver, video_path, metadata, thumbnail_path):
    self.channel = channel
    self.driver = driver
    self.video_path = video_path
    self.metadata = metadata
    self.thumbnail_path = thumbnail_path

  def upload_video(self):
    """login = YoutubeLogin('joaopedromassari1@gmail.com', 'goxgoxpgoxzgo97')
    driver = login.youtube_login()
    driver
    print("DRIVER: ", driver) """
    #TODO: Select channel to upload https://www.youtube.com/account
    uploader = YouTubeUploader(self.driver, self.video_path, self.metadata, self.thumbnail_path)
    was_video_uploaded, video_id = uploader.youtube_upload()
    assert was_video_uploaded