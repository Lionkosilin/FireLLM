import time
import yaml
import os
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from utils.data_parser import generate_sensor_data
from datetime import datetime
import random
import json

# 📁 获取配置路径（相对路径）
config_path = os.path.join(os.path.dirname(__file__), "config", "kafka_producer_config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# ✅ 配置验证提示
print("✅ Kafka Producer 配置加载完成")
print(f"🔌 Broker地址: {config['bootstrap_servers']}")
print(f"🎯 目标 Topic: {config['topic']}")
print(f"⏱️ 发送间隔: {config['send_interval']} 秒")
print("🚀 Producer 即将启动...\n")

# 🛰️ 启动 Kafka Producer
producer = None
max_retries = 10
retry_count = 0

while retry_count < max_retries:
    try:
        producer = KafkaProducer(
            bootstrap_servers=config["bootstrap_servers"],
            value_serializer=lambda v: v.encode("utf-8")
        )
        print("✅ Kafka Producer 已启动，开始发送消息...")
        break
    except NoBrokersAvailable as e:
        retry_count += 1
        print(f"⚠️ 无法连接到 Kafka，第 {retry_count} 次尝试: {e}")
        if retry_count == max_retries:
            print("❌ 达到最大重试次数，无法连接到 Kafka")
            raise
        time.sleep(5)

# 🔁 无限发送循环
while True:
    # 生成模拟传感器数据
    msg = generate_sensor_data()

    # 确保 msg 是字典类型
    if isinstance(msg, str):
        try:
            msg = json.loads(msg)  # 将字符串解析为字典
        except json.JSONDecodeError as e:
            print(f"❌ 无法解析传感器数据: {e}")
            continue

    # 添加时间戳和设备ID
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_id = f"device_{random.randint(1, 100):03d}"  # 假设设备 ID 以 device_001 到 device_100 之间随机生成

    # 将消息格式化为包含时间戳和设备 ID 的字典
    msg_with_metadata = {
        "timestamp": timestamp,
        "device_id": device_id,
        **msg  # 将生成的传感器数据加入到消息中
    }

    # 发送到 Kafka 调整为：
    try:
        producer.send(config["topic"], value=json.dumps(msg_with_metadata))  # 使用 JSON 序列化消息
        producer.flush()  # 确保消息被发送
        print(f"📤 已发送：{msg_with_metadata}")
    except Exception as e:
        print(f"❌ 消息发送异常: {e}")

    # 等待设定的时间间隔后继续发送
    time.sleep(config["send_interval"])