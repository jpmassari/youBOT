import os
import shutil
import codecs
import yt_dlp
from pydub import AudioSegment
import ffmpeg
import torch
import whisper
from whisper import utils
from googletranslate import Translator
import unicodedata
import time
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from web_driver import WebDriver
from video_uploader_rpa import YoutubeUploaderRPA
from youtube_auto_login import YoutubeLogin
from youtube_auto_upload import YouTubeUploader
from youtube_auto_channel import YoutubeChannel
from youtube_auto_google import YoutubeGoogle
import utils.clear_folders as clear_folders
from utils.reload import reload_module
from utils.clear_special_characters import remove_non_bmp_characters
from utils.yt_dlp_logger import Logger
from utils.dragon_fruit import connect_dragon, disconnect_dragon
from db.database_operations import insert_video

class Youbot:
    def __init__(self, my_channel, url, language, video_description, my_channel_id, to_language, action, translate_tags, google_email, google_password, google_country, google_profile, schedule, transcribe, shorts):
        #self.driver = driver
        self.my_channel = my_channel
        self.url = url
        self.language = language
        self.video_description = video_description
        self.metadata = []
        self.transcribe = transcribe
        self.last_google_account = ""
        self.language_mapping = {
            'English': 'en',
            'Spanish': 'es',
            'Portuguese': 'pt',
            'French': 'fr',
            'German': 'de',
            'Italian': 'it',
            'Dutch': 'nl',
            'Russian': 'ru',
            'Polish': 'pl',
            'Turkish': 'tr',
        }
        self.last_google_profile = ""
        self.current_channel = ""
        self.my_channel_id = my_channel_id 
        self.to_language = to_language 
        self.action = action
        self.translate_tags = translate_tags
        self.google_email = google_email
        self.google_password = google_password 
        self.google_country = google_country 
        self.google_profile = google_profile
        self.schedule = schedule
        self.shorts = shorts

    def normalize_filename(self, filename):
        # Normalize the filename to remove special characters
        normalized_filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('utf-8')
        
        # Replace spaces with underscores and remove other unsupported characters
        normalized_filename = normalized_filename.replace(' ', '_')
        normalized_filename = ''.join(c for c in normalized_filename if c.isalnum() or c in ['_', '-'])
        
        return normalized_filename

    def yt_dlp_hook(self, d, output):
        if d['status'] == 'finished':
            print(output)

    def download_audio(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/content/audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': Logger(),
            'progress_hooks': [lambda d: self.yt_dlp_hook(d, 'Done downloading audio, now post-processing ...')],
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
    
    def download_video(self):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': '/content/video.%(ext)s',
            'writesubtitles': False,
            'logger': Logger(),
            'progress_hooks': [lambda d: self.yt_dlp_hook(d, 'Done downloading video, now post-processing ...')],
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
    
    def get_metadata(self):
        with yt_dlp.YoutubeDL() as ydl:
            print("URL BEFORE METADATA: ", self.url)
            source_language = self.language_mapping.get(self.language, '')
            if source_language is None:
                # Display a warning to the user
                error_message = f"Warning: Language '{self.language}' is not currently supported. Please add it to the language_mapping."
                raise ValueError(error_message)
            translator = Translator(self.to_language, source_language) #'pt' is important here!
            translated_description = ""
            translated_title = ""
            translated_tags = []
            tag_limit = 0
            metadata = ydl.extract_info(self.url, False)
            #metadata = ydl.sanitize_info(metadata)
            non_bmp_title = remove_non_bmp_characters(metadata['title'])
            #non_bmp_description = remove_non_bmp_characters(metadata['description'])    
            print("ORIGINAL TAGS:  ", metadata['tags'])
            """ if 'description' in metadata and metadata['description']:
                translated_description = translator(non_bmp_description) """
            translated_title = translator(non_bmp_title)
            if(self.video_description):
                if(self.to_language != self.language_mapping.get(self.language,'')):
                    translated_description = translator(self.video_description)
            for tag in metadata['tags']:
                translated_tag = translator(tag)
                if tag_limit <= 500:
                    if(self.translate_tags == 0):
                        if(tag_limit + len(translated_tag) >= 500): break
                        translated_tags.append(translated_tag)
                        tag_limit += len(translated_tag)
                        continue
                    if(self.translate_tags == 1):
                        if(tag_limit + len(translated_tag) + len(tag) >= 500): break
                        translated_tags.append(translated_tag)
                        translated_tags.append(tag)
                        tag_limit += len(tag) + len(translated_tag)
                        continue
                    if(self.translate_tags == 2):
                        if(tag_limit + len(tag) >= 500): break
                        translated_tags.append(tag)
                        tag_limit += len(tag)
                        continue
            c = 0
            while c < len(translated_title):
                if translated_title[c] == '&' and translated_title[c + 4] == ';':
                    translated_title = translated_title[:c-1] + "'" + translated_title[c + 5:]
                c += 1

            if(self.shorts == True):
                translated_title = '#shorts ' + translated_title

            while(len(translated_title) > 100):
                words = translated_title.split().pop()
                translated_title = ' '.join(words)

            translated_metadata = {
                'title': translated_title,
                'description': f'Original youtube video: {self.url}\n{translated_description}',
                'tags': translated_tags,
            }

            return translated_metadata
    
    def transcribe_audio(self):
        device = torch.device('cuda')
        print("torch device: ", device)
        """ if(self.language == 'English'):
            model = whisper.load_model(name='tiny.en', device=device)
        else:
            model = whisper.load_model(name='tiny', device='cuda') """
        model = whisper.load_model(name='large-v2', device='cuda')

        writer = utils.get_writer('srt', '.')
        audio = whisper.load_audio('./content/audio.mp3')
        decode_options = {'language': self.to_language, 'task': self.action, 'fp16': True} #language selection for subtitles/ task: action
        result = model.transcribe(audio, word_timestamps=True, **decode_options)
        if(self.shorts == True):
            writer_options = {'highlight_words': False, 'max_line_count': 1, 'max_line_width': 50}
        else:
            writer_options = {'highlight_words': False, 'max_line_count': None, 'max_line_width': None}
        writer(result, 'suben', writer_options)
        shutil.move('suben.srt', './content')
        
        #GOOGLE TRANSLATION
        if(self.action == 'transcribe' and self.to_language != 'en'):
            translator = Translator(self.to_language)

            with open('./content/suben.srt', 'r', encoding='utf-8-sig') as infile, open(f'./content/sub{self.to_language}.srt', 'w+', encoding='utf-8') as outfile:
                for line in infile:
                    if(len(line) <= 2):
                        outfile.write(line)
                        continue
                    if(':' in line):
                        outfile.write(line)
                        continue
                    translated_line = translator(line)
                    if translated_line:
                        if (translated_line[0] != '['):
                            outfile.write(translated_line + '\n')
                            continue
                        extracted_text = (translated_line.split("'")[1])
                        #decoded_text = codecs.decode(extracted_text, 'unicode_escape')
                        #print("Decoded Text: ", decoded_text)
                        outfile.write(extracted_text + '\n')
                    else:
                        outfile.write('\n')

    def create_video(self, driver):
        self.metadata = self.get_metadata()
        #if(self.google_country == 'US'):
            #connect_dragon()
        normalized_filename = self.normalize_filename(f"{self.metadata['title']}")
        normalized_filename = f"{normalized_filename}_{self.to_language}.mkv"
        
        uploaded_files = os.listdir('./upload')
        for uploaded_file in uploaded_files:
            if(normalized_filename == uploaded_file):
                print("UPLOADED FILE MUST MATCH FILE NAME IN UPLOAD FOLDER!!: ", uploaded_file)
                self.upload_to_youtube(driver, normalized_filename)
                return

        files = os.listdir('./content')
        for file in files:
            if('video' in file):
                video_path = f'./content/{file}'
        sub_path = f'./content/sub{self.to_language}.srt'

        # Create an FFmpeg input object for the video file
        print("Verifying video_path: ", video_path)
        input_video = ffmpeg.input(video_path)
        
        custom_font_path = './font/Geist-Bold.otf'
        if(self.shorts == True):    
            subtitle_filter = f"subtitles=filename='{sub_path}':force_style='Fontname={custom_font_path},PrimaryColour=&H03fcff,FontSize=20,OutlineColour=&H4000000,BorderStyle=3,MarginV=15,"
        else:
            subtitle_filter = f"subtitles=filename='{sub_path}':force_style='Fontname={custom_font_path},PrimaryColour=&H03fcff,FontSize=20,BackColour=&H30000000,Outline=0,Shadow=0.75"

        # Use the FFmpeg overlay filter to combine the video and subtitle
        output = ffmpeg.output(
            input_video,
            os.path.join('./upload', normalized_filename), 
            vcodec='h264_nvenc', 
            acodec='copy', 
            vf=subtitle_filter,
            bitrate='25M',
            preset='slow',
            **{'y': None},
        )

        try:
            ffmpeg.run(output, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print(f"FFmpeg command failed. Stderr output:\n{e.stderr.decode('utf-8')}")
            # Add appropriate handling or raise an exception
        
        #shutil.move(normalized_filename, './upload')
        #os.unlink(normalized_filename)
        self.upload_to_youtube(driver, normalized_filename)

    def upload_to_youtube(self, driver, file_path):
        """ uploader = YouTubeUploader()
        uploader.authenticate()
        uploader.upload_video(f"./upload/{self.title}.mkv", self.title, 'teste', 'teste' ) """
        if(self.last_google_account != self.google_country):
            self.last_google_account = self.google_country
            #TODO: use google_login to create new profiles for new google accounts
            #google_login = YoutubeGoogle(self.driver, email, password)
            #google_login.youtube_google()

            #youtube_login = YoutubeLogin(self.driver, email, password)
            #youtube_login.youtube_login()
        print("MY_CHANNEL!!!: ", self.my_channel)
        """ if local_driver is None:
            youtube_channel = YoutubeChannel(self.driver, my_channel)
            youtube_channel.youtube_channel()

            uploader = YouTubeUploader(self.driver, f"./upload/{file_path}", self.metadata, None)
            video_id = uploader.youtube_upload() """
      
        youtube_channel = YoutubeChannel(driver, self.my_channel)
        try:
            youtube_channel.youtube_channel()
        except:
            youtube_channel.youtube_channel()
            
        uploader = YouTubeUploader(driver, f"./upload/{file_path}", self.metadata, self.schedule, None)
        try:
            video_id, video_url = uploader.youtube_upload()
        except:
            video_id, video_url = uploader.youtube_upload()
        insert_video(video_id, self.metadata['title'], self.url, self.my_channel_id, video_url)

    def process_video(self):
        try:
            files = os.listdir('./content')
            if not files:
                self.download_audio()
                self.download_video()
            #if(self.last_google_profile != self.google_profile):
                #self.last_google_profile = self.google_profile
            #TODO: all the process of setting up the google profile for the first time was done manually, need to automate that
            webdriver = WebDriver(headless=False, profile=self.google_profile)
            driver = webdriver.driver()
            driver.maximize_window()
            #TODO: insert languages transcribed in a list
            if(self.transcribe):
                self.transcribe_audio()
            self.create_video(driver)
            #if(self.google_country == 'US'):
                #disconnect_dragon()
            driver.quit()
            #self.upload_to_youtube("The_Origin_of_the_Natal_Nativity_Night_Raphael_Tonon_-_Catholic_Lente_Cuts.mkv")
        except Exception as e:
            print(f"An error ocurred in proccessing the video: {e}")
            driver.quit()
            return