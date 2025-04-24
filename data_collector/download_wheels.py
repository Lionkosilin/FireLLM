#!/usr/bin/env python3
"""
下载requirements.txt中指定的所有Python包到wheels目录
"""
import os
import subprocess
import sys

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    wheels_dir = os.path.join(current_dir, 'wheels')
    requirements_file = os.path.join(current_dir, 'requirements.txt')
    
    # 确保wheels目录存在
    if not os.path.exists(wheels_dir):
        os.makedirs(wheels_dir)
        print(f"✅ 创建目录: {wheels_dir}")
    
    # 执行pip下载命令
    cmd = [
        sys.executable, "-m", "pip", "download",
        "-d", wheels_dir,
        "-r", requirements_file,
        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
    ]
    
    print("⏳ 开始下载依赖包...")
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 所有依赖包已成功下载到 {wheels_dir}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 下载失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
