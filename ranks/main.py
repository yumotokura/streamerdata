from flask import Flask, render_template
from twitch_api import TwitchAPI
from youtube_api import YoutubeAPI
from openrec_api import OpenrecAPI
from common import delete_platf_pkl, read_platf_stream_data
import asyncio

app = Flask(__name__)

# インスタンスの作成
twitch_api = TwitchAPI()
youtube_api = YoutubeAPI()
openrec_api = OpenrecAPI()

# Twitch画面のルートエンドポイント
@app.route('/twitch')
def twitch():
    try:
        # Twitchデータを取得して保存
        twitch_stream_data = asyncio.run(twitch_api.twitch_get_streams())
        return render_template('twitch.html', stream_data=twitch_stream_data)
    except Exception:
        print("twitch画面取得に失敗しました")
        return render_template('twitch.html', stream_data=[])

# YouTube画面のルートエンドポイント
@app.route('/youtube')
def youtube():
    try:
        # YouTubeデータを取得して保存
        youtube_stream_data = youtube_api.youtube_get_streams()
        return render_template('youtube.html', stream_data=youtube_stream_data)
    except Exception:
        print("youtube画面取得に失敗しました")
        return render_template('youtube.html', stream_data=[])

# OpenRec画面のルートエンドポイント
@app.route('/openrec')
def openrec():
    try:
        # OpenRecデータを取得して保存
        openrec_stream_data = openrec_api.openrec_get_streams()
        return render_template('openrec.html', stream_data=openrec_stream_data)
    except Exception:
        print("openrec画面取得に失敗しました")
        return render_template('openrec.html', stream_data=[])

# メインのランキングページ
@app.route('/')
def index():
    combined_data = []
    # twitchデータを読み込む
    try:
        twitch_stream_data = asyncio.run(twitch_api.twitch_get_streams())
        combined_data += twitch_stream_data
    except Exception:
        print("twitch_get_streamsに失敗しました")
        pass
    # youtubeデータを読み込む
    try:
        youtube_data = youtube_api.youtube_get_streams()
        combined_data += youtube_data
    except Exception:
        print("youtube_get_streamsに失敗しました")
        pass
    # openrecデータを読み込む
    try:
        openrec_data = openrec_api.openrec_get_streams()
        combined_data += openrec_data
    except Exception:
        print("openrec_get_streamsに失敗しました")
        pass

    # データを結合して同時接続数の降順でソート
    for data in combined_data:
        try:
            data['viewer_count'] = int(data['viewer_count'])
        except ValueError:
            data['viewer_count'] = 0
    sorted_data = sorted(combined_data, key=lambda x: x['viewer_count'], reverse=True)

    # 上位50位までのデータを取得
    top_50_streams = sorted_data[:50]

    # テンプレートにデータを渡してレンダリング
    return render_template('index.html', stream_data=top_50_streams)

if __name__ == '__main__':
    app.run(debug=True)
