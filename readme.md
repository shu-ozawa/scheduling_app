docker build -t schenv .

docker run -v /c/Users/shuic/Desktop/schoolie/scheduling_app:/scheduling_app -p 8501:8501 schenv
