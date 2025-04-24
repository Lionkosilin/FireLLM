from sqlalchemy import create_engine, Column, Float, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import os

# 创建基础模型
Base = declarative_base()

class SensorData(Base):
    """传感器数据表模型"""
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    smoke = Column(Float, nullable=False)

def get_db_session():
    """获取数据库会话"""
    try:
        # 获取环境变量或使用默认值
        db_user = os.getenv('DB_USER', 'firellm')
        db_password = os.getenv('DB_PASSWORD', 'firellm123')
        db_host = os.getenv('DB_HOST', 'postgres')
        db_name = os.getenv('DB_NAME', 'sensordata')
        
        # 创建数据库连接
        db_url = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'
        engine = create_engine(db_url)
        
        # 创建表（如果不存在）
        Base.metadata.create_all(engine)
        
        # 创建会话
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        raise

def parse_sensor_data(data_str):
    """将字符串格式的传感器数据解析为Python对象"""
    try:
        # 处理 Python 字符串形式的字典数据
        if data_str.startswith("{'") and data_str.endswith("'}"):
            # 将单引号字符串转换为合法的 JSON
            data_str = data_str.replace("'", "\"")
        
        # 解析 JSON 数据
        data = json.loads(data_str)
        return data
    except json.JSONDecodeError:
        print(f"❌ 无法解析数据: {data_str}")
        return None
    except Exception as e:
        print(f"❌ 数据处理错误: {str(e)}")
        return None
