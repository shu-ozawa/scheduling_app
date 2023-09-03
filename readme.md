# 初期設定
環境の作成は以下のコードを実行  

docker build -t schenv .


# 実行
以下のコードを実行  
パスは適宜変更

Win  
docker run -v /c/Users/shuic/Desktop/schoolie/scheduling_app:/scheduling_app -p 8501:8501 schenv

Mac  
docker run -v /Users/shu/Desktop/scheduling_app:/scheduling_app -p 8501:8501 schenv
