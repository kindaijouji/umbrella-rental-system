# FlaskというWebアプリケーションフレームワークをインポートします。jsonifyはPythonオブジェクトをJSON形式に変換する関数です。
from flask import Flask, jsonify

# CORSは異なるドメインからのリクエストを許可するためのライブラリです。
# 例：localhost:3000のReactアプリからlocalhost:5000のPythonサーバーにアクセスする時に必要です。
from flask_cors import CORS

# NFCカードを読み取るためのライブラリをインポートします
import nfc

# 時間関連の機能を使うためのライブラリをインポートします（sleep関数など）
import time

# 正規表現を使うためのライブラリをインポートします（文字列から特定のパターンを見つけるのに使います）
import re

# NFCカード読み取り時のエラーを処理するためのクラスをインポートします
from nfc.tag.tt3 import Type3TagCommandError

# 並行処理を行うためのThreadクラスをインポートします
from threading import Thread

# Flaskアプリケーションを作成します
app = Flask(__name__)

# CORSを有効にして、異なるドメインからのアクセスを許可します
CORS(app)

# 最新の学籍番号を保存するためのグローバル変数を初期化します
# このグローバル変数は、NFCリーダーが読み取った最新の学籍番号を保持します
latest_student_id = None

# カードから読み取ったテキストから12桁の数字を抽出する関数です
def extract_12_digit_numbers(text):
    # テキストを'|'で分割し、右側の部分を取り出してスペースを削除します
    # '|'がない場合は元のテキストをそのまま使用します
    ascii_text = text.split('|')[1].strip() if '|' in text else text
    
    # 正規表現を使って12桁の数字を探します
    matches = re.findall(r'\d{12}', ascii_text)
    
    # 見つかった12桁の数字の3桁目以降を返します（最初の2桁を除外）
    return [match[2:] for match in matches]

# NFCカードが接続された時に呼び出される関数です
def connected(tag):
    # グローバル変数を使用することを宣言します
    global latest_student_id
    
    try:
        # カードの内容をダンプ（読み取り）します
        dumps = tag.dump()
        
        # System FE00セクションを見つけるためのフラグを初期化します
        fe00_section = False
        
        # ダンプした各行を処理します
        for line in dumps:
            # System FE00セクションの開始を見つけたらフラグを立てます
            if "System FE00" in line:
                fe00_section = True
            # FE00セクション内で'0000:'で始まる行を見つけたら学籍番号を抽出します
            elif fe00_section and '0000:' in line:
                numbers = extract_12_digit_numbers(line)
                if numbers:
                    latest_student_id = numbers[0]
                    print("Found student ID:", latest_student_id)
            # 次のSystemセクションが始まったら処理を終了します
            elif fe00_section and line.startswith("System"):
                break
                
    # カード読み取りエラーが発生した場合の処理
    except Type3TagCommandError as e:
        print("カードの読み取りエラー:", e)
        return False
    # その他の予期せぬエラーが発生した場合の処理
    except Exception as e:
        print("予期せぬエラー:", e)
        return False
    
    # 正常に処理が完了したことを示すためTrueを返します
    return True

# NFCリーダーを継続的に監視するループ関数です
def nfc_reader_loop():
    # 無限ループで実行し続けます
    while True:
        try:
            # NFCリーダーに接続します
            with nfc.ContactlessFrontend('usb') as clf:
                # カードの接続を待ち受けます
                tag = clf.connect(rdwr={
                    'on-connect': connected,  # カード接続時に呼び出す関数
                    'iterations': 1,          # 1回だけ試行
                    'interval': 0.1           # 0.1秒間隔でチェック
                })
                
            # カードが検出されなかった場合のメッセージを表示
            if tag is None:
                print("カードを検出できませんでした")
        # リーダーでエラーが発生した場合の処理
        except Exception as e:
            print("リーダーエラー:", e)
        
        # 1秒待機してから次のループを開始
        time.sleep(1)

# Webアプリケーションのエンドポイント（URLパス）を定義します
# /latest-id にアクセスすると最新の学籍番号を取得できます
@app.route('/latest-id')
def get_latest_id():
    # 最新の学籍番号をJSON形式で返します
    return jsonify({'student_id': latest_student_id})

# このファイルが直接実行された場合（インポートされた場合は実行されません）
if __name__ == '__main__':
    # NFCリーダーのループを別スレッドで開始します
    # daemon=Trueにすることで、メインプログラムが終了したら自動的に終了します
    nfc_thread = Thread(target=nfc_reader_loop, daemon=True)
    nfc_thread.start()
    
    # Flaskサーバーを起動します
    # host='0.0.0.0'で外部からのアクセスを許可し、ポート5000で待ち受けます
    app.run(host='0.0.0.0', port=5000)