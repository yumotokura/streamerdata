import os
import configparser
from googleapiclient.discovery import build
import re

class YoutubeAPI:
    """
    クラス概要：
        YoutubeAPIを扱うクラスです

    クラス詳細：
        YoutubeAPIを扱うクラスです
        Youtubeで配信中の上位50名の情報を取得します。
    """
    def __init__(self) -> None:
        """
        メソッド概要:
            初期化時にインスタンス変数を設定

        メソッド詳細:
            初期化時にインスタンス変数を設定

        :param ytb_strm_list: Youtube配信者情報のリスト
        :type ytb_strm_list: list
        :param api_key: api_key認証情報
        :type api_key: str
        """
        self.ytb_strm_list = []
        self.api_key = None
        self.get_configini()

    def get_configini(self) -> str:
        """
        メソッド概要:
            youtubeAPIの設定ファイルの読み込みを行う

        メソッド詳細:
            config.iniからyoutubeAPIの認証情報を取得する
            ※common.pyに統一予定
        """
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        inifile = configparser.ConfigParser()
        inifile.read(config_file_path)
        self.api_key = inifile.get('YOUTUBE', 'API_KEY')

    def youtube_get_streams(self) -> list:
        """
        メソッド概要:
            youtubeから上位50件の配信者情報を取得する

        メソッド詳細:
            youtubeAPIを使用し、上位50件の配信者情報を返却する

        :return self.ytb_strm_list: youtube配信者情報のlist
        :rtype self.ytb_strm_list: list
        """
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

            if len(streams_list) >= 50:
                break

        # 視聴者数で降順ソート
        streams_list.sort(key=lambda x: int(x['viewer_count']) if x['viewer_count'].isdigit() else 0, reverse=True)

        # 読み込んだデータをインスタンス変数に保存
        self.ytb_strm_list = streams_list
        return self.ytb_strm_list

    def get_channel_info(self, youtube, channel_id: str) -> dict:
        """
        メソッド概要:
            channel_id に対応するYouTubeチャンネルの詳細情報を取得しプロフィール画像を取得する

        メソッド詳細:
            youtubeAPIのchannelsメソッドを使用しYouTubeチャンネルの詳細情報を取得する
            ※youtubeAPIのsearchメソッドではプロフィール画像は取得不可のため

        :param youtube: Youtubeインスタンス
        :type youtube: instance
        :param channel_id: youtubeのチャンネルID
        :type channel_id: str

        :return response: YouTubeチャンネルの詳細情報
        :rtype response: dict
        """
        request = youtube.channels().list(
            part='snippet,brandingSettings',
            id=channel_id
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]
        else:
            return None

    def get_viewer_count(self, youtube, video_id: str) -> dict:
        """
        メソッド概要:
            video_id に対応するライブ配信の詳細情報を取得する

        メソッド詳細:
            video_id に対応するライブ配信の詳細情報を取得する

        :param youtube: Youtubeインスタンス
        :type youtube: instance
        :param video_id: 配信ID
        :type video_id: str

        :return response: ライブ配信に関する詳細情報
        :rtype response: dict
        """
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
        
    def contains_japanese(self, text: str) -> str:
        """
        メソッド概要:
            日本語を含むかどうかを判定する正規表現。
            ※これを実施しないと海外の配信が含まれてしまう。

        メソッド詳細:
            日本語を含むかどうかを判定する正規表現。

        :param text: 配信情報
        :type text: str

        :return text: 判定後の配信情報
        :rtype text: str
        """
        return bool(re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text))
