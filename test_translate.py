#!/usr/bin/env python3
"""
测试翻译功能，定位proxies错误
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_translate():
    """测试翻译功能"""
    try:
        print("开始测试翻译功能...")
        
        # 导入相关模块
        from alibabacloud_alimt20181012.client import Client as alimt20181012Client
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_alimt20181012 import models as alimt_20181012_models
        from alibabacloud_tea_util import models as util_models
        
        print("✅ 模块导入成功")
        
        # 获取环境变量
        ali_access_key_id = os.environ.get('ALI_CLOUD_ACCESS_KEY_ID')
        ali_access_key_secret = os.environ.get('ALI_CLOUD_ACCESS_KEY_SECRET')
        
        if not ali_access_key_id or not ali_access_key_secret:
            print("❌ 环境变量未设置")
            return
            
        print(f"✅ 环境变量获取成功: {ali_access_key_id[:10]}...")
        
        # 创建配置
        print("创建配置对象...")
        config = open_api_models.Config(
            access_key_id=ali_access_key_id,
            access_key_secret=ali_access_key_secret
        )
        config.endpoint = 'mt.aliyuncs.com'
        print("✅ 配置对象创建成功")
        
        # 创建客户端
        print("创建客户端...")
        client = alimt20181012Client(config)
        print("✅ 客户端创建成功")
        
        # 创建翻译请求
        print("创建翻译请求...")
        translate_request = alimt_20181012_models.TranslateGeneralRequest(
            format_type='text',
            source_language='en',
            target_language='zh',
            source_text='Hello, world!',
            scene='general'
        )
        runtime = util_models.RuntimeOptions()
        print("✅ 翻译请求创建成功")
        
        # 执行翻译
        print("执行翻译...")
        response = client.translate_general_with_options(translate_request, runtime)
        
        # 详细输出响应信息
        print(f"响应体: {response.body}")
        print(f"响应体类型: {type(response.body)}")
        
        # 检查响应体的具体属性
        if hasattr(response.body, 'code'):
            print(f"错误代码: {response.body.code}")
        if hasattr(response.body, 'message'):
            print(f"错误消息: {response.body.message}")
        if hasattr(response.body, 'request_id'):
            print(f"请求ID: {response.body.request_id}")
        if hasattr(response.body, 'data'):
            print(f"数据: {response.body.data}")
        
        if response.body and hasattr(response.body, 'data') and response.body.data:
            translated_text = response.body.data.translated
            print(f"✅ 翻译成功: {translated_text}")
        else:
            print("❌ 翻译失败: 响应体为空或格式不正确")
            if response.body:
                print(f"响应体属性: {dir(response.body)}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print(f"错误类型: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_translate() 