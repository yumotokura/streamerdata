import requests

class OpenrecAPI:
    """
    クラス概要：
        OpenrecAPIを扱うクラスです

    クラス詳細：
        OpenrecAPIを扱うクラスです
        Openrecで配信中の上位50名の情報を取得します。
    """
    def __init__(self) -> None:
        """
        メソッド概要:
            初期化時にインスタンス変数を設定

        メソッド詳細:
            初期化時にインスタンス変数を設定
            
        :param oprc_strm_list: Openrec配信者情報のリスト
        :type oprc_strm_list: list
        """
        self.oprc_strm_list = []

    def openrec_get_streams(self):
        """
        メソッド概要:
            openrecから上位50件の配信者情報を取得する

        メソッド詳細:
            openrecAPIを使用し、上位50件の配信者情報を返却する

        :return self.oprc_strm_list: openrec配信者情報のlist
        :rtype self.oprc_strm_list: list
        """
        # リクエストURL設定
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
                # 取得したデータから必要な情報に絞る
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

                    # Openrecではリアルタイムで50名以上の配信者がいない場合がある
                    # if len(streams_list) >= 50:
                    #     break

                # 読み込んだデータをインスタンス変数に保存
                self.oprc_strm_list = streams_list
                return self.oprc_strm_list

            except Exception as e:
                print(f"データの処理中にエラーが発生しました: {e}")
        else:
            print(f"OpenRec API からデータの取得中にエラーが発生しました: {response.status_code} {response.reason}")
