#!/usr/bin/env python
"""
Django REST APIのテスト
"""
import os
import sys
import django
import json
from io import BytesIO
from PIL import Image
import numpy as np

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from inference.models import MLApp

def create_test_image_file():
    """テスト用画像ファイルを作成"""
    # 224x224のランダム画像
    image_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    image = Image.fromarray(image_array, 'RGB')
    
    # バイトストリームに保存
    img_buffer = BytesIO()
    image.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=img_buffer.getvalue(),
        content_type='image/jpeg'
    )

def test_api_endpoints():
    """REST APIエンドポイントをテスト"""
    print("🌐 Django REST APIテスト開始...")
    
    client = Client()
    
    # 1. MLアプリ一覧取得
    print("\n📋 MLアプリ一覧取得:")
    response = client.get('/api/ml-apps/')
    if response.status_code == 200:
        apps = response.json()
        results = apps.get('results', apps) if 'results' in apps else apps
        print(f"  ✅ {len(results)}個のアプリを取得")
        for app in results:
            print(f"    - {app['name']} (ID: {app['id']}, Device: {app['device_type']})")
    else:
        print(f"  ❌ エラー: {response.status_code}")
    
    # 2. デバイス情報取得（最初のアプリから）
    print("\n💻 デバイス情報取得:")
    app = MLApp.objects.first()
    if app:
        response = client.post(f'/api/ml-apps/{app.id}/device_info/')
        if response.status_code == 200:
            device_info = response.json()
            print("  ✅ デバイス情報:")
            for key, value in device_info.items():
                print(f"    {key}: {value}")
        else:
            print(f"  ❌ エラー: {response.status_code}")
    else:
        print("  ❌ テスト用MLアプリが見つかりません")
    
    # 3. 画像予測API
    print("\n🖼️ 画像予測APIテスト:")
    test_image = create_test_image_file()
    
    # 最初のMLアプリを取得
    app = MLApp.objects.first()
    if app:
        response = client.post(f'/api/ml-apps/{app.id}/predict/', {
            'image': test_image
        })
        
        if response.status_code == 200:
            result = response.json()
            print("  ✅ 予測成功:")
            print(f"    予測クラス: {result['predicted_class']}")
            print(f"    信頼度: {result['confidence']:.4f}")
            print(f"    処理時間: {result['processing_time']:.4f}秒")
            print(f"    デバイス: {result['device']}")
        else:
            print(f"  ❌ 予測エラー: {response.status_code}")
            print(f"    レスポンス: {response.content.decode()}")
    else:
        print("  ❌ テスト用MLアプリが見つかりません")
    
    # 4. ベンチマークAPI
    print("\n⚡ ベンチマークAPIテスト:")
    if app:
        response = client.post(f'/api/ml-apps/{app.id}/benchmark/', {
            'iterations': 10
        })
        
        if response.status_code == 200:
            result = response.json()
            benchmark = result.get('benchmark', result)
            print("  ✅ ベンチマーク成功:")
            print(f"    平均処理時間: {benchmark['average_time_per_inference']:.4f}秒")
            print(f"    スループット: {benchmark['throughput_fps']:.2f} FPS")
            print(f"    総時間: {benchmark['total_time']:.4f}秒")
        else:
            print(f"  ❌ ベンチマークエラー: {response.status_code}")
            print(f"    レスポンス: {response.content.decode()}")
    
    print("\n✅ Django REST APIテスト完了！")

if __name__ == "__main__":
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"❌ APIテストエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
