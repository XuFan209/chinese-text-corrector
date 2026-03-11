#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文文本纠错系统 - 快速启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_python():
    """检查Python版本"""
    print("=" * 60)
    print("中文文本纠错系统 - 启动器")
    print("=" * 60)
    
    version = sys.version_info
    print(f"\nPython版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        input("按回车键退出...")
        sys.exit(1)
    
    print("✓ Python版本检查通过")
    return True

def check_dependencies():
    """检查必要的依赖"""
    print("\n检查依赖...")
    
    required = ['flask', 'pycorrector', 'docx', 'docx2txt', 'torch', 'transformers']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (未安装)")
            missing.append(package)
    
    if missing:
        print(f"\n缺少依赖: {', '.join(missing)}")
        print("正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✓ 依赖安装完成")
        except Exception as e:
            print(f"✗ 安装失败: {e}")
            print("请手动运行: pip install -r requirements.txt")
            input("按回车键退出...")
            sys.exit(1)
    else:
        print("✓ 所有依赖已安装")
    
    return True

def check_model():
    """检查模型文件"""
    print("\n检查模型...")
    
    import os
    import pycorrector
    
    site_packages = os.path.dirname(os.path.dirname(pycorrector.__file__))
    model_path = os.path.join(site_packages, 'macbert4csc-base-chinese')
    
    if not os.path.exists(model_path):
        print(f"✗ 模型未找到: {model_path}")
        print("请确保模型文件已下载到 site-packages 目录")
        input("按回车键退出...")
        sys.exit(1)
    
    required_files = ['config.json', 'pytorch_model.bin', 'vocab.txt']
    missing = [f for f in required_files if not os.path.exists(os.path.join(model_path, f))]
    
    if missing:
        print(f"✗ 模型文件不完整，缺少: {', '.join(missing)}")
        input("按回车键退出...")
        sys.exit(1)
    
    print(f"✓ 模型已就绪")
    return True

def start_server():
    """启动服务"""
    print("\n" + "=" * 60)
    print("启动服务...")
    print("=" * 60)
    
    # 导入并启动Flask应用
    try:
        from app import app
        print("\n服务启动成功！")
        print("-" * 60)
        print("访问地址: http://127.0.0.1:8080")
        print("-" * 60)
        print("按 Ctrl+C 停止服务\n")
        
        # 自动打开浏览器
        time.sleep(1)
        webbrowser.open('http://127.0.0.1:8080')
        
        # 启动Flask服务
        app.run(host='0.0.0.0', port=8080, debug=False)
        
    except Exception as e:
        print(f"\n✗ 启动失败: {e}")
        input("按回车键退出...")
        sys.exit(1)

def main():
    """主函数"""
    try:
        check_python()
        check_dependencies()
        check_model()
        start_server()
    except KeyboardInterrupt:
        print("\n\n服务已停止")
        sys.exit(0)

if __name__ == '__main__':
    main()
