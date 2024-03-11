docker run -it \
-v "$(pwd):/home/app" \
-p 5000:5000 \
-e PORT=5000 \
getaround python app.py