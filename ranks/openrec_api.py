import requests

class OpenrecAPI:
    """
    メソッド概要：
        OpenrecAPIを扱うクラスです

    メソッド詳細：
        OpenrecAPIを扱うクラスです
    """
    def __init__(self) -> None:
        # 初期化時にインスタンス変数を設定
        self.openrec_streams_list = []

    def openrec_get_streams(self):
        url = 'https://public.openrec.tv/external/api/v5/movies'
        params = {
            'is_live': True,
            'onair_status': 1,
            'sort': 'total_views',
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            streams_list = []
            try:
                data = response.json()
                for item in data:
                    stream_dict = {
                        'user_name': item['channel']['nickname'],
                        'title': item['title'],
                        'viewer_count': item['live_views'],
                        'stream_url': f"https://www.openrec.tv/live/{item['id']}",
                        'profile_image_url': item['channel']['icon_image_url'],
                        'thumbnail_url': item['thumbnail_url']
                    }
                    streams_list.append(stream_dict)

                # 読み込んだデータをインスタンス変数に保存
                self.openrec_streams_list = streams_list
                return self.openrec_streams_list

            except Exception as e:
                print(f"データの処理中にエラーが発生しました: {e}")
        else:
            print(f"OpenRec API からデータの取得中にエラーが発生しました: {response.status_code} {response.reason}")
