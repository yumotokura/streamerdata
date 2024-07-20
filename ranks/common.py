import os
import pandas as pd

# 現在のファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))

def delete_platf_pkl(platf: str):
    fpath = os.path.join(current_dir, f'{platf}_top_streams.pkl')
    if os.path.exists(fpath):
        os.remove(fpath)

def read_platf_stream_data(platf: str):
    fpath = os.path.join(current_dir, f'{platf}_top_streams.pkl')
    if os.path.exists(fpath):
        df = pd.read_pickle(fpath)
        return df.to_dict(orient='records')