# FireLLM 项目介绍

## 项目概述

FireLLM 是一个基于流处理的火灾风险检测系统，采用了现代化的分布式架构设计。该系统通过接收、处理和分析来自各种传感器的实时数据流，利用 Apache Flink 和深度学习模型进行火灾风险评估，最终通过可视化工具呈现监控结果，并对潜在的火灾风险发出警报。

## 系统架构

系统采用微服务架构，主要由以下组件构成：

### 数据层

- **Kafka**：作为消息队列，负责接收和分发传感器数据
- **PostgreSQL**：持久化存储处理后的数据，用于查询和分析
- **Zookeeper**：为 Kafka 提供协调服务

### 处理层

- **Apache Flink**：分布式流处理框架，处理和分析实时数据
  - JobManager：负责作业调度和资源分配
  - TaskManager：执行具体的数据处理任务

### 模型服务层

- **TorchServe**：部署和服务深度学习模型
  - 使用火灾检测模型分析传感器数据，提高检测精度

### 监控与可视化层

- **Prometheus**：收集和存储监控指标
- **Grafana**：可视化监控数据，提供交互式仪表盘

## 数据流

1. **数据采集**：传感器数据通过数据生产者发送到 Kafka (`sensor-data` 和 `flink-input` 主题)
2. **实时处理**：Flink 作业从 Kafka 消费数据，分析潜在火灾风险
   - 基本规则：温度 > 35℃ 且湿度 < 40%，或烟雾浓度 > 0.7 时判定为火灾风险
   - 高级分析：通过 TorchServe 深度学习模型进行更精确的预测
3. **结果输出**：处理结果写回 Kafka (`flink-output` 或 `model-output` 主题)
4. **数据存储**：数据消费者将结果持久化到 PostgreSQL 数据库
5. **监控与报警**：Prometheus 收集系统指标，Grafana 展示系统状态和警报

## 核心功能

### 火灾检测算法

```python
def process_data(data):
    try:
        record = json.loads(data)
        temperature = float(record.get('temperature', 0.0))
        humidity = float(record.get('humidity', 0.0))
        smoke = float(record.get('smoke', 0.0))
        
        # 基于规则的火灾风险判断
        is_fire_risk = (temperature > 35.0 and humidity < 40.0) or smoke > 0.7

        result = {
            'timestamp': record.get('timestamp', ''),
            'device_id': record.get('device_id', 'unknown'),
            'temperature': temperature,
            'humidity': humidity,
            'smoke': smoke,
            'is_fire_risk': is_fire_risk,
            'alert_level': 'HIGH' if is_fire_risk else 'NORMAL'
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            'error': f"处理数据时出错: {str(e)}",
            'original_data': data
        })
```

### 模型集成

系统支持将基础规则检测与深度学习模型结合，通过与 TorchServe 集成，实现更精确的火灾检测：

```python
def call_model_api(data):
    try:
        response = requests.post(TORCHSERVE_URL, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f" 模型API调用失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f" 模型API调用异常: {e}")
        return None
```

## 部署指南

系统使用 Docker Compose 进行容器化部署，简化了环境配置和服务管理。

### 前置条件

- Docker 和 Docker Compose
- 足够的系统资源 (推荐 8GB+ RAM)

### 部署步骤

1. **清理环境**（如果需要重新部署）：
   ```bash
   docker compose down -v --remove-orphans
   ```

2. **启动服务**：
   ```bash
   docker compose up -d
   ```

3. **访问监控界面**：
   - Grafana：`http://<host>:3000` (默认用户名/密码: admin/admin)
   - Flink Dashboard：`http://<host>:8081`
   - Prometheus：`http://<host>:9090`

## 系统监控

系统提供了丰富的监控指标：

1. **Flink 作业监控**：任务状态、吞吐量、延迟等
2. **Kafka 监控**：主题消息数量、消费延迟等
3. **系统资源监控**：CPU、内存、网络使用情况

## 技术栈

- **流处理**：Apache Flink 1.17.2
- **消息队列**：Kafka 3.4
- **数据存储**：PostgreSQL 14
- **模型部署**：TorchServe
- **监控**：Prometheus + Grafana
- **容器化**：Docker & Docker Compose
- **编程语言**：Python 3.10

## 项目结构

- **data_collector/**：数据生产者和消费者实现
- **flink_processor/**：Flink 作业定义和配置
- **integration/**：模型集成代码
- **torchserve/**：深度学习模型服务
- **prometheus/**, **grafana/**：监控系统配置
- **docker-compose.yml**：容器编排配置

## 扩展与优化

- 增加更多传感器类型的支持
- 优化火灾检测算法，减少误报
- 添加用户界面，提供更直观的监控与交互
- 实施告警通知系统
- 扩展水平扩展能力，支持更大规模的数据处理

## 故障排除

- **服务启动问题**：检查 docker-compose.yml 中的网络配置
- **数据流中断**：验证 Kafka 连接和主题配置
- **Flink 作业失败**：查看 Flink Dashboard 中的异常日志

## 结语

FireLLM 项目展示了如何利用现代化的流处理技术和深度学习实现实时火灾风险监测。该系统具有高可扩展性、低延迟和高可靠性特点，适合应用于各类火灾预警场景。
