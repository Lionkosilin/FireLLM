FROM python:3.10-slim

WORKDIR /app

# 安装依赖
RUN pip install apache-flink==1.17.0 kafka-python==2.0.2 requests==2.31.0

# 复制应用程序
COPY ./integration /app

# 运行应用
CMD ["python", "fire_detection_with_model.py"]
