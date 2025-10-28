# コンセプト

## bookmark\export_bookmarks.py
- GoogleのブックマークをCドライブ配下のブックマーク記録用ファイルから、転記してCSVファイルにまとめる。


## search_history.js 
- Googleの検索履歴をJSON形式にしたファイルを下記からダウンロード
  -- https://takeout.google.com/ ※他のYoutubeなどの閲覧履歴も確認可能

- 加工して、sqliteに格納(検索時間, URL, Title, URLに応じたタグ)
- 1: sqliteからデータを抜き取る
  -- 履歴復元用のJSONファイルを作成する
  -- データに付けたタグをベースにmatplotlibにて、どのタグのURLをどのくらい閲覧したか、
     どの日にどのくらい閲覧したかグラフにする
    -- そのうえでメールにてグラフ添付して発報する
