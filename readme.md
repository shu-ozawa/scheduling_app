# 0. 初期設定
## 実行環境の作成

scheduling_appフォルダを1度左クリックして選択し、再度右クリックして、「ターミナルで開く」を選択してください。  
そこで、以下のコードを実行します。
  
docker build -t schenv .

## フォルダの作成

PDFファイルを格納するフォルダを"2_Student_schedule_PDF"のなかに、"schedulePDF_result"という名前で作成してください。  

# 1. スケジュール作成手順

## 1.1 実行環境を動かす

scheduling_appフォルダを1度左クリックして選択し、再度右クリックして、「ターミナルで開く」を選択してください。  
そこで、以下のコードを実行します。

Win  
docker run -v /c/Users/shuic/Desktop/schoolie/scheduling_app:/scheduling_app -p 8501:8501 schenv

Mac  
docker run -v /Users/shu/Desktop/scheduling_app:/scheduling_app -p 8501:8501 schenv

## 1.2 ブラウザでスケジュールを実行する

以下のリンクを選択して、スケジュールを実行してください。  
  
http://localhost:8501/


# 2. 修了するとき（厳密にやらなくてもよいはず）

## 2.1 実行環境の停止

もし、さきほど開いたターミナルが開いてなければ、scheduling_appフォルダを1度左クリックして選択し、再度右クリックして、「ターミナルで開く」を選択してください。  
そこで、以下のコードを実行します。  
  
docker stop $(docker ps -q)

あとはすべてのウィンドウは閉じてしまって大丈夫です。