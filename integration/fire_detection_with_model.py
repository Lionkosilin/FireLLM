import json
import os
import time
import requests
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common import Configuration

# TorchServe API 端点
TORCHSERVE_URL = "http://torchserve:8080/predictions/fire_detector"  # 使用Docker服务名

def call_model_api(data):
    """
    调用TorchServe API进行预测
    """
    try:
        response = requests.post(
            TORCHSERVE_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API调用失败: HTTP {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求模型API出错: {e}")
        return None

def process_data_with_model(data):
    """
    处理数据并调用模型进行预测
    """
    print(f"🟡 正在处理数据: {data}")
    
    try:
        # 解析输入数据
        record = json.loads(data)
        temperature = float(record.get('temperature', 0.0))
        humidity = float(record.get('humidity', 0.0))
        smoke = float(record.get('smoke', 0.0))
        device_id = record.get('device_id', 'unknown')
        timestamp = record.get('timestamp', '')
        
        # 过滤异常数据
        is_abnormal = temperature > 60.0 or smoke > 0.8
        
        # 只有异常数据才发送到模型
        if is_abnormal:
            # 调用模型API
            model_result = call_model_api(data)
            
            if model_result:
                # 合并模型预测结果与原始数据
                result = {
                    'timestamp': timestamp,
                    'device_id': device_id,
                    'temperature': temperature,
                    'humidity': humidity,
                    'smoke': smoke,
                    'is_abnormal': is_abnormal,
                    'model_prediction': model_result,
                    'alert_level': model_result.get('risk_level', 'HIGH')
                }
            else:
                # 如果模型调用失败，使用基本逻辑
                result = {
                    'timestamp': timestamp,
                    'device_id': device_id,
                    'temperature': temperature,
                    'humidity': humidity,
                    'smoke': smoke,
                    'is_abnormal': is_abnormal,
                    'alert_level': 'HIGH',
                    'model_failed': True
                }
                
            print(f"✅ 处理完成: {result}")
            return json.dumps(result)
        else:
            # 正常数据不处理
            return None
            
    except Exception as e:
        print(f"❌ 错误处理数据: {e}")
        return json.dumps({
            'error': f"处理数据时出错: {str(e)}",
            'original_data': data
        })

def main():
    print("🚀 初始化 Flink 环境...")
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    print("🔌 设置 Kafka Source...")
    kafka_consumer = FlinkKafkaConsumer(
        topics='flink-input',
        deserialization_schema=SimpleStringSchema(),
        properties={
            'bootstrap.servers': 'kafka:9092',
            'group.id': 'fire-detection-group'
        }
    )
    
    print("🎯 设置 Kafka Sink...")
    kafka_producer = FlinkKafkaProducer(
        topic='model-output',  # 使用新的主题存储模型处理后的结果
        serialization_schema=SimpleStringSchema(),
        producer_config={
            'bootstrap.servers': 'kafka:9092',
            'transaction.timeout.ms': '5000'
        }
    )
    
    print("🔁 绑定数据流...")
    data_stream = env.add_source(kafka_consumer)
    
    # 使用模型处理数据
    processed_stream = data_stream.map(
        process_data_with_model, 
        output_type=Types.STRING()
    ).filter(lambda x: x is not None)  # 过滤正常数据
    
    # 将结果发送到Kafka
    processed_stream.add_sink(kafka_producer)
    
    # 尝试多次启动执行计划（处理网络问题）
    max_retries = 10
    for attempt in range(max_retries):
        try:
            print("🏁 启动执行计划...")
            env.execute("Fire Detection with Model Integration Job")
            print("✅ Flink 作业执行完毕！")
            break
        except Exception as e:
            print(f"⚠️ 启动失败，第 {attempt + 1} 次尝试: {e}")
            time.sleep(10)
    else:
        print("❌ 多次尝试后仍未成功启动 Flink Job")

if __name__ == '__main__':
    print("📄 启动 fire_detection_with_model.py 脚本")
    main()
