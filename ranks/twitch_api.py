import os
import configparser
from twitchAPI.twitch import Twitch

class TwitchAPI:
    """
    メソッド概要：
        TwitchAPIを扱うクラスです

    メソッド詳細：
        TwitchAPIを扱うクラスです
    """
    def __init__(self) -> None:
        # 初期化時にインスタンス変数を設定
        self.global_streams_list = []
        self.clientID = None
        self.secretID = None
        self.get_configini()

    def get_configini(self) -> str:
        # twitchAPIの設定ファイルの読み込み
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        inifile = configparser.ConfigParser()
        inifile.read(config_file_path)

        self.clientID = inifile.get('TWITCH', 'CLIENT_ID')
        self.secretID = inifile.get('TWITCH', 'SECRET_ID')

    async def twitch_get_streams(self) -> None:
        # twitchAPIの設定ファイルの読み込み
        twitch = await Twitch(self.clientID, self.secretID)
        await twitch.authenticate_app([])

        # ストリームの一覧取得（上位50件）
        streams_list = []
        i = 1
        async for stream in twitch.get_streams(language='ja'):
            stream_dict = stream.to_dict()
            user_id = stream_dict['user_id']
            
            # ユーザーIDからユーザー情報を取得
            user_info = []
            async for user in twitch.get_users(user_ids=[user_id]):
                user_info.append(user.to_dict())

            if user_info:
                user_data = user_info[0]
                user_name = user_data['login']  # 正しいユーザー名を取得
                
                # 配信URLを追加
                stream_dict['stream_url'] = f"https://www.twitch.tv/{user_name}"
                
                # 配信者のアイコン情報を追加
                if 'profile_image_url' in user_data:
                    stream_dict['profile_image_url'] = user_data['profile_image_url']
                else:
                    stream_dict['profile_image_url'] = 'https://via.placeholder.com/150'  # デフォルトの画像URL
                            
                # サムネイルURLを追加
                if 'thumbnail_url' in stream_dict:
                    thumbnail_url = stream_dict['thumbnail_url']
                    stream_dict['thumbnail_url'] = thumbnail_url.replace('{width}', '320').replace('{height}', '180')
                else:
                    stream_dict['thumbnail_url'] = 'https://via.placeholder.com/320x180'  # デフォルトのサムネイル画像URL
                
                streams_list.append(stream_dict)
            
            if i >= 50:
                break
            i += 1

        # 読み込んだデータをグローバル変数に保存
        self.global_streams_list = streams_list
        await twitch.close()
        return self.global_streams_list


