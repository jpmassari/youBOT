import os
import shutil
import codecs
import yt_dlp
from pydub import AudioSegment
import ffmpeg
import whisper
from whisper import utils
from googletranslate import Translator
import unicodedata
import time

from video_uploader_rpa import YoutubeUploaderRPA

class Youbot:
    def __init__(self, driver, url, language, action, to_language):
        self.driver = driver
        self.url = url
        self.metadata = self.get_metadata()
        self.language = language
        self.action = action
        self.to_language = to_language

    def normalize_filename(self, filename):
        # Normalize the filename to remove special characters
        normalized_filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('utf-8')
        
        # Replace spaces with underscores and remove other unsupported characters
        normalized_filename = normalized_filename.replace(' ', '_')
        normalized_filename = ''.join(c for c in normalized_filename if c.isalnum() or c in ['_', '-'])
        
        return normalized_filename

    def download_audio(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/content/audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }], 
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
    
    def download_video(self):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': '/content/video.%(ext)s',
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
    
    def get_metadata(self):
        with yt_dlp.YoutubeDL() as ydl:
            metadata = ydl.extract_info(self.url, False)
            print("METADA: ", metadata)
            metadata = {
                'title': metadata['title'],
                'description': metadata['description'],
                'tags': ['teste','teste2','test3'], #alterar para as tags do video original
            }
            print("normalized metadata: ",metadata)
            return metadata
    
    def transcribe_audio(self):
        model = whisper.load_model(name='large-v2', device='cuda')

        writer = utils.get_writer('srt', '.')
        audio = whisper.load_audio('./content/audio.mp3')
        decode_options = {'language': self.language, 'task': self.action} #language selection for subtitles
        result = model.transcribe(audio, word_timestamps=True, **decode_options)
        writer_options = {'highlight_words': False, 'max_line_count': None, 'max_line_width': None}
        writer(result, 'sub', writer_options)
        shutil.move('./sub.srt', './content')
        if(self.action == 'translate' and self.to_language != 'en'):
            translator = Translator(self.to_language)
            with open('./content/sub.srt', 'r', encoding='utf-8-sig') as infile, open(f'./content/sub{self.to_language}.srt', 'w+', encoding='utf-8') as outfile:
                for line in infile:
                    print("infile: ", infile)
                    if(len(line) <= 2):
                        outfile.write(line)
                        continue
                    if(':' in line):
                        outfile.write(line)
                        continue
                    translated_line = translator(line)
                    if translated_line:
                        print("translated line: ", translated_line)
                        print("translted_line[0]: ", translated_line[0])
                        if (translated_line[0] != '['):
                            print("OI")
                            outfile.write(translated_line + '\n')
                            continue
                        extracted_text = (translated_line.split("'")[1])
                        print("extracted_text: ",extracted_text)
                        """ decoded_text = codecs.decode(extracted_text, 'unicode_escape')
                        print("Decoded Text: ", decoded_text) """
                        outfile.write(extracted_text + '\n')
                    else:
                        outfile.write('\n')

    def create_video(self):
        files = os.listdir('./content')
        for file in files:
            if('video' in file):
                video_path = f'./content/{file}'
        sub_path = f'./content/sub{self.to_language}.srt'

        # Create an FFmpeg input object for the video file
        input_video = ffmpeg.input(video_path)

        # Create an FFmpeg input object for the subtitle file
        subtitle_filter = f"subtitles=filename='{sub_path}':force_style='Fontsize=22,PrimaryColour=\\&Hffffff,SecondaryColour=\\&Hffffff'"
        normalized_filename = self.normalize_filename(f"{self.metadata['title']}")
        normalized_filename = f"{normalized_filename}.mkv"
        # Use the FFmpeg overlay filter to combine the video and subtitle
        output = ffmpeg.output(input_video, normalized_filename, vcodec='h264_nvenc', acodec='copy', vf=subtitle_filter)

        ffmpeg.run(output)
        shutil.move(normalized_filename, './upload')
        time.sleep(5)
        self.upload_to_youtube(normalized_filename)

    def upload_to_youtube(self, file_path):
        """ uploader = YouTubeUploader()
        uploader.authenticate()
        uploader.upload_video(f"./upload/{self.title}.mkv", self.title, 'teste', 'teste' ) """
        print("METADATA: ", self.metadata)
        uploader = YoutubeUploaderRPA(None, self.driver, f"./upload/{file_path}", self.metadata, None)
        uploader.upload_video()
    
    def process_video(self):
        #self.download_audio()
        #self.download_video()
        self.transcribe_audio()
        self.create_video()