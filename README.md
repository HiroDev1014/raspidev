# raspidev
Raspberry Pi ダッシュボード
天気・時刻・ニュースを表示するシンプルなFlaskダッシュボードです。

必要なもの
Python 3.8+
インターネット接続
セットアップ
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. サーバーを起動
python app.py
アクセス
ブラウザで以下を開く：

http://localhost:5000
同じネットワーク上の別デバイスからアクセスする場合：

http://<Raspberry PiのIPアドレス>:5000
IPアドレスの確認方法：

hostname -I
自動起動の設定（オプション）
起動時に自動でサーバーを立ち上げたい場合は cron に追加：

crontab -e
以下を追加（パスは適宜修正）：

@reboot cd /home/pi/dashboard && python app.py >> /home/pi/dashboard/app.log 2>&1 &
カスタマイズ
天気の都市変更: app.py の get_weather("Tokyo") を変更（例: "Osaka", "Sapporo"）
ニュースフィードの変更: get_news() の feed_url を任意のRSSフィードURLに変更
更新頻度
項目	更新間隔
時刻	1秒ごと
天気	5分ごと
ニュース	10分ごと
使用API
天気: Open-Meteo（無料・APIキー不要）
ニュース: NHKニュース RSS（デフォルト）
