import socket
import time
import os
import subprocess

def wait_for_kafka(host, port, timeout=60):
    print(f"🔄 Waiting for Kafka at {host}:{port} ...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("✅ Kafka is available.")
                return True
        except (OSError, ConnectionRefusedError) as e:
            print(f"⚠️ Kafka 连接失败: {e}")
            time.sleep(1)
    raise RuntimeError("❌ Timeout: Kafka is not reachable")

def create_topics(topics):
    for topic in topics:
        print(f"📦 Creating topic: {topic}")
        try:
            subprocess.run([
                "/opt/bitnami/kafka/bin/kafka-topics.sh",
                "--create",
                "--if-not-exists",
                "--bootstrap-server", "kafka:9092",
                "--replication-factor", "1",
                "--partitions", "1",
                "--topic", topic
            ], check=True)
        except FileNotFoundError:
            print("⚠️ Kafka CLI not found in this container. Skipping topic creation.")
            return

def wait_for_postgres(host, port, timeout=60):
    print(f"🔄 Waiting for PostgreSQL at {host}:{port} ...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("✅ PostgreSQL is available.")
                return True
        except (OSError, ConnectionRefusedError) as e:
            print(f"⚠️ PostgreSQL 连接失败: {e}")
            time.sleep(1)
    raise RuntimeError("❌ Timeout: PostgreSQL is not reachable")

if __name__ == "__main__":
    kafka_host = "kafka"
    kafka_port = 9092
    postgres_host = "postgres" 
    postgres_port = 5432
    role = os.getenv("RUN_ROLE", "consumer")
    script = os.getenv("SCRIPT", "kafka_consumer.py")

    # 等待Kafka可用
    wait_for_kafka(kafka_host, kafka_port)

    # 仅 producer 容器负责创建 topic
    if role == "producer":
        create_topics([
            "sensor-data",
            "flink-input",
            "flink-output"
        ])
    
    # 消费者和Flink处理器需要等待数据库可用
    if role in ["consumer", "flink-processor"]:
        wait_for_postgres(postgres_host, postgres_port)

    print(f"🚀 Starting {script}")
    os.execvp("python", ["python", script])