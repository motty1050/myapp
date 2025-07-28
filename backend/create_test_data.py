#!/usr/bin/env python
import os
import sys
import django
import json

# Django設定の初期化
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from inference.models import MLApp

def create_test_data():
    """テストデータを作成"""
    
    # 既存のデータをクリア
    MLApp.objects.all().delete()
    print("Cleared existing data")
    
    # CUDA対応の画像分類アプリを作成
    cuda_app = MLApp.objects.create(
        name="CUDA高速画像分類",
        description="CUDA対応の高速画像分類アプリ（猫 vs 犬）",
        app_type="image_classification",
        device_type="auto", 
        classes=json.dumps(["cat", "dog"]),
        batch_size=4,
        use_mixed_precision=True,
        model_optimization=json.dumps({
            "quantization": False,
            "tensorrt": False,
            "onnx": False
        })
    )
    print(f"✅ Created CUDA app: {cuda_app.id} - {cuda_app.name}")
    
    # CPU専用アプリを作成
    cpu_app = MLApp.objects.create(
        name="CPU画像分類",
        description="CPU専用の画像分類アプリ（軽量版）",
        app_type="image_classification",
        device_type="cpu",
        classes=json.dumps(["cat", "dog"]),
        batch_size=1,
        use_mixed_precision=False,
        model_optimization=json.dumps({
            "quantization": True,
            "tensorrt": False,
            "onnx": True
        })
    )
    print(f"✅ Created CPU app: {cpu_app.id} - {cpu_app.name}")
    
    # 混合精度テスト用アプリ
    mixed_app = MLApp.objects.create(
        name="混合精度テストアプリ",
        description="混合精度を使用したベンチマーク用アプリ",
        app_type="image_classification",
        device_type="auto",
        classes=json.dumps(["cat", "dog", "bird", "fish"]),
        batch_size=8,
        use_mixed_precision=True,
        model_optimization=json.dumps({
            "quantization": False,
            "tensorrt": True,
            "onnx": False
        })
    )
    print(f"✅ Created mixed precision app: {mixed_app.id} - {mixed_app.name}")
    
    # すべてのアプリを表示
    apps = MLApp.objects.all()
    print(f"\n📊 Total apps created: {apps.count()}")
    print("="*50)
    
    for app in apps:
        print(f"ID: {app.id}")
        print(f"Name: {app.name}")
        print(f"Device: {app.device_type}")
        print(f"Classes: {app.classes}")
        print(f"Batch size: {app.batch_size}")
        print(f"Mixed precision: {app.use_mixed_precision}")
        print(f"Created: {app.created_at}")
        print("-" * 30)

if __name__ == "__main__":
    create_test_data()
