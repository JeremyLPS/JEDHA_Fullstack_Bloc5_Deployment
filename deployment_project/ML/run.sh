docker run -it \
-v "$(pwd):/home/app" \
-e MLFLOW_TRACKING_URI="https://jedha-fullstack-deployment-a1e3f74298ba.herokuapp.com/" \
-e AWS_ACCESS_KEY_ID="AKIAUP7OJ727UIDJNFHV" \
-e AWS_SECRET_ACCESS_KEY="woXDKD1mOnwXse+zWvo1XYspzwfYEsBudx+kunRDi" \
-e BACKEND_STORE_URI="postgresql://udps6utt6o09cu:p976db0f4d297d5fcd854608c4751a6f982ebacb95ba608d56013d0f363820a25@ceu9lmqblp8t3q.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d20cc2jf8i866f" \
-e ARTIFACT_ROOT="s3://jedha-fullstack-deployment/artefacts/" \
mlflow_trainings python app.py
