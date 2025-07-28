#!/usr/bin/env python
"""
CUDA推論システムのテスト
"""
import os
import sys
import django
from PIL import Image
import numpy as np

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from inference.cuda_inference import CUDAImageClassifier, get_classifier

def create_test_image():
    """テスト用の画像を作成"""
    # 224x224のランダム画像を作成
    image_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    image = Image.fromarray(image_array, 'RGB')
    return image

def test_cuda_inference():
    """CUDA推論システムをテスト"""
    print("🚀 CUDA推論システムテスト開始...")
    
    # 1. デバイス情報確認
    print("\n📱 デバイス情報:")
    classifier = get_classifier('auto')
    device_info = classifier.get_device_info()
    for key, value in device_info.items():
        print(f"  {key}: {value}")
    
    # 2. 単一画像推論テスト
    print("\n🖼️ 単一画像推論テスト:")
    test_image = create_test_image()
    result = classifier.predict(test_image)
    
    print(f"  予測クラス: {result['predicted_class']}")
    print(f"  信頼度: {result['confidence']:.4f}")
    print(f"  処理時間: {result['processing_time']:.4f}秒")
    print(f"  デバイス: {result['device']}")
    print(f"  クラス確率: {result['class_probabilities']}")
    
    # 3. バッチ推論テスト
    print("\n📦 バッチ推論テスト:")
    test_images = [create_test_image() for _ in range(4)]
    batch_results = classifier.predict_batch(test_images, batch_size=2)
    
    for i, result in enumerate(batch_results):
        print(f"  画像{i+1}: {result['predicted_class']} (信頼度: {result['confidence']:.4f})")
    
    # 4. ベンチマークテスト
    print("\n⚡ ベンチマークテスト:")
    benchmark = classifier.benchmark(num_iterations=20)
    print(f"  総処理時間: {benchmark['total_time']:.4f}秒")
    print(f"  平均処理時間: {benchmark['average_time_per_inference']:.4f}秒")
    print(f"  スループット: {benchmark['throughput_fps']:.2f} FPS")
    print(f"  デバイス: {benchmark['device']}")
    
    # 5. CPU vs CUDA比較（利用可能な場合）
    print("\n🔄 デバイス比較テスト:")
    
    # CPU分類器
    cpu_classifier = CUDAImageClassifier(device_type='cpu')
    cpu_result = cpu_classifier.predict(test_image)
    print(f"  CPU処理時間: {cpu_result['processing_time']:.4f}秒")
    
    # CUDA分類器（利用可能な場合）
    try:
        cuda_classifier = CUDAImageClassifier(device_type='cuda')
        cuda_result = cuda_classifier.predict(test_image)
        print(f"  CUDA処理時間: {cuda_result['processing_time']:.4f}秒")
        speedup = cpu_result['processing_time'] / cuda_result['processing_time']
        print(f"  高速化倍率: {speedup:.2f}x")
    except Exception as e:
        print(f"  CUDA利用不可: {e}")
    
    print("\n✅ CUDA推論システムテスト完了！")

if __name__ == "__main__":
    try:
        test_cuda_inference()
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
