import json
import os
import time
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common import Configuration

def process_data(data):
    print(f"🟡 正在处理数据: {data}")  # ✅ 调试用：打印每条数据
    try:
        record = json.loads(data)
        temperature = float(record.get('temperature', 0.0))
        humidity = float(record.get('humidity', 0.0))
        smoke = float(record.get('smoke', 0.0))
        device_id = record.get('device_id', 'unknown')
        timestamp = record.get('timestamp', '')

        is_fire_risk = (temperature > 35.0 and humidity < 40.0) or smoke > 0.7

        result = {
            'timestamp': timestamp,
            'device_id': device_id,
            'temperature': temperature,
            'humidity': humidity,
            'smoke': smoke,
            'is_fire_risk': is_fire_risk,
            'alert_level': 'HIGH' if is_fire_risk else 'NORMAL'
        }

        print(f"✅ 处理完成: {result}")  # ✅ 调试用：打印结果
        return json.dumps(result)

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
        topic='flink-output',
        serialization_schema=SimpleStringSchema(),
        producer_config={
            'bootstrap.servers': 'kafka:9092',
            'transaction.timeout.ms': '5000'
        }
    )

    print("🔁 绑定数据流...")
    data_stream = env.add_source(kafka_consumer)
    processed_stream = data_stream.map(process_data, output_type=Types.STRING())
    processed_stream.add_sink(kafka_producer)

    max_retries = 10
    for attempt in range(max_retries):
        try:
            print("🏁 启动执行计划...")
            env.execute("Fire Detection Job")
            print("✅ Flink 作业执行完毕！")
            break
        except Exception as e:
            print(f"⚠️ 启动失败，第 {attempt + 1} 次尝试: {e}")
            time.sleep(10)
    else:
        print("❌ 多次尝试后仍未成功启动 Flink Job")


if __name__ == '__main__':
    print("📄 启动 fire_detection.py 脚本")
    main()