# 初期設定
環境の作成は以下のコードを実行  

docker build -t schenv .


# 実行
以下のコードを実行  

docker run -v /c/Users/shuic/Desktop/schoolie/scheduling_app:/scheduling_app -p 8501:8501 schenv
