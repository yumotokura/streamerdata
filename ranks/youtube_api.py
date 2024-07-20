import os
import configparser
from googleapiclient.discovery import build
import re

class YoutubeAPI:
    """
    メソッド概要：
        YoutubeAPIを扱うクラスです

    メソッド詳細：
        YoutubeAPIを扱うクラスです
    """
    def __init__(self) -> None:
        # 初期化時にインスタンス変数を設定
        self.global_streams_list = []
        self.api_key = None
        self.get_configini()

    def get_configini(self) -> str:
        # 設定ファイルの読み込み
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        inifile = configparser.ConfigParser()
        inifile.read(config_file_path)
        self.api_key = inifile.get('YOUTUBE', 'API_KEY')

    def youtube_get_streams(self):
        youtube = build('youtube', 'v3', developerKey=self.api_key)
        
        streams_list = []
        next_page_token = None

        request = youtube.search().list(
            part='snippet',
            eventType='live',
            type='video',
            regionCode='JP',
            relevanceLanguage='ja',
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        
        for item in response['items']:
            stream_dict = {}
            stream_dict['user_name'] = item['snippet']['channelTitle']
            stream_dict['title'] = item['snippet']['title']
            stream_dict['stream_url'] = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            stream_dict['description'] = item['snippet']['description']
            
            # チャンネル情報を取得してプロフィール画像をセットする
            channel_id = item['snippet']['channelId']
            channel_info = self.get_channel_info(youtube, channel_id)
            stream_dict['profile_image_url'] = channel_info['snippet']['thumbnails']['default']['url']
            
            # 視聴者数を取得する
            viewer_count = self.get_viewer_count(youtube, item['id']['videoId'])
            stream_dict['viewer_count'] = viewer_count

            # サムネイル画像をセットする
            stream_dict['thumbnail_url'] = f"https://img.youtube.com/vi/{item['id']['videoId']}/mqdefault.jpg"

            # タイトルと説明文に日本語が含まれているかチェック
            if self.contains_japanese(stream_dict['title']) and self.contains_japanese(stream_dict['description']):
                streams_list.append(stream_dict)

            if len(streams_list) >= 150:
                break

        # 視聴者数で降順ソート
        streams_list.sort(key=lambda x: int(x['viewer_count']) if x['viewer_count'].isdigit() else 0, reverse=True)

        # 読み込んだデータをグローバル変数に保存
        self.global_streams_list = streams_list
        return self.global_streams_list

    def get_channel_info(self, youtube, channel_id):
        request = youtube.channels().list(
            part='snippet,brandingSettings',
            id=channel_id
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]
        else:
            return None

    def get_viewer_count(self, youtube, video_id):
        request = youtube.videos().list(
            part='liveStreamingDetails',
            id=video_id
        )
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            item = response['items'][0]
            live_details = item['liveStreamingDetails']
            
            # 視聴者数を取得
            viewer_count = live_details['concurrentViewers'] if 'concurrentViewers' in live_details else "N/A"
            return viewer_count
        else:
            return "N/A"
        
    def contains_japanese(self, text):
        # 日本語を含むかどうかを判定する正規表現
        return bool(re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text))
