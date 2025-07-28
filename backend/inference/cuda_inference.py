"""
CUDA対応画像分類推論サービス
"""
import time
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2
from PIL import Image
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CUDAImageClassifier:
    """CUDA対応画像分類器"""
    
    def __init__(self, model_path: Optional[str] = None, device_type: str = 'auto'):
        self.device_type = device_type
        self.device = self._get_device()
        self.model = None
        self.transform = None
        self.classes = []
        self.loaded = False
        
        # デフォルトの前処理設定
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        if model_path:
            self.load_model(model_path)
        else:
            self._create_default_model()
            
    def _get_device(self) -> torch.device:
        """最適なデバイスを選択"""
        if self.device_type == 'auto':
            if torch.cuda.is_available():
                device = torch.device('cuda')
                logger.info(f"CUDA device selected: {torch.cuda.get_device_name(0)}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = torch.device('mps')
                logger.info("MPS device selected (Apple Silicon)")
            else:
                device = torch.device('cpu')
                logger.info("CPU device selected")
        else:
            device = torch.device(self.device_type)
            logger.info(f"Manual device selected: {device}")
            
        return device
    
    def _create_default_model(self):
        """デフォルトの軽量モデルを作成（デモ用）"""
        logger.info("Creating default MobileNetV2 model for demo")
        
        # MobileNetV2ベースの軽量モデル
        self.model = mobilenet_v2(pretrained=True)
        
        # 2クラス分類用にカスタマイズ（猫 vs 犬）
        num_features = self.model.classifier[1].in_features
        self.model.classifier[1] = nn.Linear(num_features, 2)
        
        # デモ用クラス
        self.classes = ['cat', 'dog']
        
        # モデルをデバイスに移動
        self.model.to(self.device)
        self.model.eval()
        
        # 混合精度対応
        if self.device.type == 'cuda':
            self.model = self.model.half()  # FP16に変換
            
        self.loaded = True
        logger.info(f"Default model loaded on {self.device}")
    
    def load_model(self, model_path: str):
        """学習済みモデルを読み込み"""
        try:
            model_path = Path(model_path)
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                self._create_default_model()
                return
                
            # モデル情報を読み込み
            model_info_path = model_path.parent / 'model_info.json'
            if model_info_path.exists():
                with open(model_info_path, 'r') as f:
                    model_info = json.load(f)
                    self.classes = model_info.get('classes', ['class_0', 'class_1'])
            
            # PyTorchモデルを読み込み
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # モデル構造を復元
            if 'model_type' in checkpoint and checkpoint['model_type'] == 'mobilenet_v2':
                self.model = mobilenet_v2(pretrained=False)
                num_features = self.model.classifier[1].in_features
                self.model.classifier[1] = nn.Linear(num_features, len(self.classes))
            else:
                # デフォルトモデルにフォールバック
                self._create_default_model()
                return
                
            # 学習済み重みを読み込み
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            # 混合精度対応
            if self.device.type == 'cuda':
                self.model = self.model.half()
                
            self.loaded = True
            logger.info(f"Model loaded from {model_path} on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._create_default_model()
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """画像の前処理"""
        # RGBに変換
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # 前処理適用
        tensor = self.transform(image)
        
        # バッチ次元を追加
        tensor = tensor.unsqueeze(0)
        
        # デバイスに移動
        tensor = tensor.to(self.device)
        
        # 混合精度対応
        if self.device.type == 'cuda':
            tensor = tensor.half()
            
        return tensor
    
    def predict(self, image: Image.Image) -> Dict:
        """画像分類の推論実行"""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
            
        start_time = time.time()
        
        try:
            # 前処理
            input_tensor = self.preprocess_image(image)
            
            # 推論実行
            with torch.no_grad():
                if self.device.type == 'cuda':
                    # CUDA最適化
                    with torch.cuda.amp.autocast():
                        outputs = self.model(input_tensor)
                else:
                    outputs = self.model(input_tensor)
                
                # 確率計算
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                # CPUに移動して値を取得
                confidence = confidence.cpu().item()
                predicted_class_idx = predicted.cpu().item()
                predicted_class = self.classes[predicted_class_idx]
                
                # 全クラスの確率
                all_probs = probabilities.cpu().numpy()[0]
                class_probs = {
                    self.classes[i]: float(prob) 
                    for i, prob in enumerate(all_probs)
                }
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
        
        processing_time = time.time() - start_time
        
        return {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'class_probabilities': class_probs,
            'processing_time': processing_time,
            'device': str(self.device)
        }
    
    def predict_batch(self, images: List[Image.Image], batch_size: int = 8) -> List[Dict]:
        """バッチ推論（CUDA効率化）"""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
            
        results = []
        
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i + batch_size]
            start_time = time.time()
            
            try:
                # バッチ前処理
                batch_tensors = []
                for img in batch_images:
                    tensor = self.preprocess_image(img)
                    batch_tensors.append(tensor)
                
                batch_input = torch.cat(batch_tensors, dim=0)
                
                # バッチ推論
                with torch.no_grad():
                    if self.device.type == 'cuda':
                        with torch.cuda.amp.autocast():
                            outputs = self.model(batch_input)
                    else:
                        outputs = self.model(batch_input)
                    
                    probabilities = torch.nn.functional.softmax(outputs, dim=1)
                    confidences, predicted = torch.max(probabilities, 1)
                    
                    # 結果を個別に処理
                    for j in range(len(batch_images)):
                        confidence = confidences[j].cpu().item()
                        predicted_class_idx = predicted[j].cpu().item()
                        predicted_class = self.classes[predicted_class_idx]
                        
                        probs = probabilities[j].cpu().numpy()
                        class_probs = {
                            self.classes[k]: float(prob) 
                            for k, prob in enumerate(probs)
                        }
                        
                        processing_time = (time.time() - start_time) / len(batch_images)
                        
                        results.append({
                            'predicted_class': predicted_class,
                            'confidence': confidence,
                            'class_probabilities': class_probs,
                            'processing_time': processing_time,
                            'device': str(self.device)
                        })
                        
            except Exception as e:
                logger.error(f"Batch prediction error: {e}")
                # エラー時は個別処理にフォールバック
                for img in batch_images:
                    try:
                        result = self.predict(img)
                        results.append(result)
                    except:
                        results.append({
                            'predicted_class': 'error',
                            'confidence': 0.0,
                            'class_probabilities': {},
                            'processing_time': 0.0,
                            'device': str(self.device),
                            'error': str(e)
                        })
        
        return results
    
    def get_device_info(self) -> Dict:
        """デバイス情報を取得"""
        info = {
            'device_type': str(self.device),
            'device_name': str(self.device)
        }
        
        if self.device.type == 'cuda':
            info.update({
                'cuda_available': torch.cuda.is_available(),
                'cuda_device_count': torch.cuda.device_count(),
                'cuda_device_name': torch.cuda.get_device_name(0),
                'cuda_memory_total': f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB",
                'cuda_memory_allocated': f"{torch.cuda.memory_allocated() / 1024**3:.1f}GB",
                'cuda_memory_cached': f"{torch.cuda.memory_reserved() / 1024**3:.1f}GB"
            })
        elif self.device.type == 'mps':
            info.update({
                'mps_available': torch.backends.mps.is_available()
            })
            
        return info
    
    def benchmark(self, num_iterations: int = 100) -> Dict:
        """推論速度ベンチマーク"""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
            
        # ダミー画像作成
        dummy_image = Image.new('RGB', (224, 224), color='red')
        
        # ウォームアップ
        for _ in range(10):
            self.predict(dummy_image)
            
        # ベンチマーク実行
        start_time = time.time()
        for _ in range(num_iterations):
            self.predict(dummy_image)
            
        total_time = time.time() - start_time
        avg_time = total_time / num_iterations
        throughput = num_iterations / total_time
        
        return {
            'total_time': total_time,
            'average_time_per_inference': avg_time,
            'throughput_fps': throughput,
            'device': str(self.device),
            'iterations': num_iterations
        }

# グローバルインスタンス（シングルトン）
_classifier_instance = None

def get_classifier(device_type: str = 'auto') -> CUDAImageClassifier:
    """グローバル分類器インスタンスを取得"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = CUDAImageClassifier(device_type=device_type)
    return _classifier_instance

def reset_classifier():
    """分類器インスタンスをリセット"""
    global _classifier_instance
    _classifier_instance = None
