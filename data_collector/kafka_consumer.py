import yaml
import os
from kafka import KafkaConsumer
from utils.db_models import get_db_session, SensorData
from datetime import datetime
import json
import time
from kafka import KafkaProducer

# 📁 获取配置路径（相对路径）
config_path = os.path.join(os.path.dirname(__file__), "config", "kafka_producer_config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# 尝试连接数据库
db_session = None
max_retries = 10
retry_count = 0
print("⏳ 尝试连接数据库...")
while retry_count < max_retries:
    try:
        db_session = get_db_session()
        print("✅ 数据库连接成功")
        break
    except Exception as e:
        retry_count += 1
        print(f"⚠️ 数据库连接失败，第 {retry_count} 次尝试: {str(e)}")
        if retry_count == max_retries:
            print("❌ 数据库连接失败，达到最大尝试次数")
            raise
        time.sleep(5)

# Kafka 生产者 - 用于将处理过的数据发送到 Flink 处理
flink_producer = KafkaProducer(
    bootstrap_servers=config["bootstrap_servers"],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ✅ 创建消费者
consumer = KafkaConsumer(
    config["topic"],
    bootstrap_servers=config["bootstrap_servers"],
    auto_offset_reset='earliest',
    group_id='fire-monitoring-consumer',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))  # 直接解析JSON
)
print("✅ Kafka 消费者已启动：监听 Topic ->", config["topic"])
print("⏳ 等待 Producer 发送消息中...")

# 🔁 循环监听
for message in consumer:
    try:
        # 获取消息值（已经是解析后的字典）
        data = message.value
        print(f"📩 收到消息：{data}")
        
        # 创建传感器数据记录
        sensor_record = SensorData(
            device_id=data.get('device_id', 'unknown'),
            timestamp=datetime.strptime(data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 
                                    "%Y-%m-%d %H:%M:%S"),
            temperature=float(data.get('temperature', 0.0)),
            humidity=float(data.get('humidity', 0.0)),
            smoke=float(data.get('smoke', 0.0))
        )
        
        # 保存到数据库
        db_session.add(sensor_record)
        db_session.commit()
        print(f"💾 数据已保存到数据库: {data}")
        
        # 将数据转发到用于 Flink 处理的主题
        try:
            flink_producer.send("flink-input", value=data)  # 直接发送数据字典
            flink_producer.flush()  # 确保消息被转发
            print(f"🔄 数据已转发到 flink-input 主题")
        except Exception as e:
            print(f"❌ 转发到 flink-input 异常: {e}")
            
    except Exception as e:
        print(f"❌ 处理消息时出错: {str(e)}")
        if db_session:
            db_session.rollback()