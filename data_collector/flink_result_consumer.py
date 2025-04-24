import yaml
import os
import json
from kafka import KafkaConsumer
from utils.db_models import get_db_session
import requests
from datetime import datetime

# 📁 获取配置路径（相对路径）
config_path = os.path.join(os.path.dirname(__file__), "config", "kafka_producer_config.yaml")

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# 获取数据库连接
db_session = get_db_session()

# ✅ 创建消费者，监听Flink输出
flink_consumer = KafkaConsumer(
    "flink-output",
    bootstrap_servers=config["bootstrap_servers"],
    auto_offset_reset='earliest',
    group_id='flink-result-consumer',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

print("✅ Flink结果消费者已启动：监听 Topic -> flink-output")
print("⏳ 等待Flink处理结果...")

# 将检测到火灾风险的数据发送到推理服务
def send_to_inference_service(data):
    try:
        # 实际项目中，这里会调用 TorchServe 进行推理
        response = requests.post(
            "http://torchserve:8080/predictions/fire_model",
            json=data
        )
        print(f"🔍 推理服务响应: {response.status_code}")
        return response.json()
    except Exception as e:
        print(f"❌ 调用推理服务失败: {str(e)}")
        return None

# 🔁 循环监听
for message in flink_consumer:
    try:
        data = message.value
        print(f"📊 收到Flink处理结果: {data}")
        
        # 判断是否为火灾风险
        if data.get("is_fire_risk", False):
            print(f"🚨 检测到火灾风险! 设备: {data.get('device_id')}")
            
            # 调用推理服务进一步确认
            inference_result = send_to_inference_service(data)
            if inference_result and inference_result.get("confirmed_risk", False):
                print(f"🔥 推理服务确认火灾风险! 警报级别: {inference_result.get('risk_level', 'HIGH')}")
                
                # 触发报警系统、通知管理员等操作
            
    except Exception as e:
        print(f"❌ 处理Flink结果时出错: {str(e)}")
