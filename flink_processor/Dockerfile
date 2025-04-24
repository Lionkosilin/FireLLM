FROM flink:1.17.2

# 安装 Python3、pip、编译工具（容器内联网安装）
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev build-essential && \
    ln -s /usr/bin/python3 /usr/bin/python

# 拷贝本地 wheels 包和 requirements
COPY wheels /opt/flink/wheels
COPY requirements.txt /opt/flink/

# ✅ 下载 Kafka Connector jar（确保兼容 Flink 1.17.2）
RUN wget -O /opt/flink/lib/kafka-clients-2.8.0.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/2.8.0/kafka-clients-2.8.0.jar
# 下载 flink-connector-kafka-1.17.0.jar
RUN wget -O /opt/flink/lib/flink-connector-kafka-1.17.0.jar \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/1.17.0/flink-connector-kafka-1.17.0.jar

# 安装 Python 依赖（使用本地 wheel，无需联网）
RUN pip3 install --no-index --find-links=/opt/flink/wheels -r /opt/flink/requirements.txt

# 设置 PYTHONPATH（如有需要）
ENV PYTHONPATH=$PYTHONPATH:/opt/flink/lib

# 拷贝代码目录并设置工作路径
WORKDIR /opt/flink/job
COPY . /opt/flink/job/
RUN chmod +x /opt/flink/job/fire_detection.py

# 启动脚本（使用 shell 包装以记录日志和实现重试）

# 替换 CMD 为 ENTRYPOINT 以确保启动脚本生效
ENTRYPOINT ["bash", "-c", "\
echo '📄 启动 fire_detection.py 脚本' && \
while true; do \
    python3 /opt/flink/job/fire_detection.py >> /opt/flink/job/fire_detection.log 2>&1; \
    echo '⚠️ 脚本异常退出，10秒后重启...' >> /opt/flink/job/fire_detection.log; \
    sleep 10; \
done"]