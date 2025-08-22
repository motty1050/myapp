import time
import random
import logging
from io import BytesIO
from PIL import Image
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse

from .models import MLApp, PredictionLog, ImageUpload
from .serializers import MLAppSerializer, PredictionInputSerializer, PredictionOutputSerializer, PredictionLogSerializer
from .cuda_inference import get_classifier

logger = logging.getLogger(__name__)

@api_view(['GET'])
def api_root(request):
    """API情報ルート"""
    return Response({
        'message': 'ML推論API',
        'version': '1.0.0',
        'endpoints': {
            'ml_apps': '/api/ml-apps/',
            'logs': '/api/logs/',
            'admin': '/admin/',
        },
        'available_actions': {
            'predict': 'POST /api/ml-apps/{id}/predict/',
            'batch_predict': 'POST /api/ml-apps/{id}/predict_batch/',
            'device_info': 'GET /api/ml-apps/{id}/device_info/',
            'benchmark': 'POST /api/ml-apps/{id}/benchmark/',
        },
        'status': 'running'
    })

class MLAppViewSet(viewsets.ReadOnlyModelViewSet):
    """ML アプリの一覧・詳細取得"""
    queryset = MLApp.objects.filter(is_active=True)
    serializer_class = MLAppSerializer
    parser_classes = [MultiPartParser, JSONParser]

    @action(detail=True, methods=['post'])
    def predict(self, request, pk=None):
        """特定のMLアプリで推論を実行"""
        ml_app = self.get_object()
        
        # 画像分類以外はまだ未対応
        if ml_app.app_type != 'image_classification':
            return Response({
                'error': f'App type {ml_app.app_type} is not yet supported'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 画像ファイルの確認
        if 'image' not in request.FILES:
            return Response({
                'error': 'Image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        try:
            # 画像を開く
            image = Image.open(image_file)
            
            # CUDA分類器を取得
            classifier = get_classifier(device_type=ml_app.device_type)
            
            # 推論実行
            start_time = time.time()
            result = classifier.predict(image)
            processing_time = time.time() - start_time
            
            # ログ保存
            prediction_log = PredictionLog.objects.create(
                ml_app=ml_app,
                input_data={
                    'filename': image_file.name,
                    'size': image_file.size,
                    'format': image.format or 'Unknown'
                },
                output_data=result,
                confidence_score=result.get('confidence', 0.0),
                predicted_class=result.get('predicted_class', 'unknown'),
                processing_time=processing_time
            )
            
            # 画像保存
            image_upload = ImageUpload.objects.create(
                prediction_log=prediction_log,
                image=image_file,
                original_filename=image_file.name,
                file_size=image_file.size,
                image_width=image.width,
                image_height=image.height
            )
            
            # レスポンス構築
            response_data = {
                'prediction_id': prediction_log.id,
                'ml_app': ml_app.name,
                'predicted_class': result['predicted_class'],
                'confidence': result['confidence'],
                'class_probabilities': result['class_probabilities'],
                'processing_time': processing_time,
                'device': result['device'],
                'image_info': {
                    'width': image.width,
                    'height': image.height,
                    'format': image.format,
                    'mode': image.mode
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return Response({
                'error': f'Prediction failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])  
    def predict_batch(self, request, pk=None):
        """バッチ推論（複数画像を一度に処理）"""
        ml_app = self.get_object()
        
        if ml_app.app_type != 'image_classification':
            return Response({
                'error': f'App type {ml_app.app_type} is not yet supported'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 複数画像ファイルの確認
        images = request.FILES.getlist('images')
        if not images:
            return Response({
                'error': 'At least one image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(images) > 10:  # 一度に10枚まで
            return Response({
                'error': 'Maximum 10 images allowed per batch'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 画像を開く
            pil_images = []
            image_infos = []
            
            for img_file in images:
                image = Image.open(img_file)
                pil_images.append(image)
                image_infos.append({
                    'filename': img_file.name,
                    'size': img_file.size,
                    'width': image.width,
                    'height': image.height,
                    'format': image.format
                })
            
            # CUDA分類器を取得
            classifier = get_classifier(device_type=ml_app.device_type)
            
            # バッチ推論実行
            start_time = time.time()
            batch_results = classifier.predict_batch(
                pil_images, 
                batch_size=ml_app.get_optimal_batch_size()
            )
            total_processing_time = time.time() - start_time
            
            # 結果とログ保存
            results = []
            for i, (result, img_file, img_info) in enumerate(zip(batch_results, images, image_infos)):
                # ログ保存
                prediction_log = PredictionLog.objects.create(
                    ml_app=ml_app,
                    input_data=img_info,
                    output_data=result,
                    confidence_score=result.get('confidence', 0.0),
                    predicted_class=result.get('predicted_class', 'unknown'),
                    processing_time=result.get('processing_time', 0.0)
                )
                
                # 画像保存
                ImageUpload.objects.create(
                    prediction_log=prediction_log,
                    image=img_file,
                    original_filename=img_file.name,
                    file_size=img_file.size,
                    image_width=img_info['width'],
                    image_height=img_info['height']
                )
                
                results.append({
                    'prediction_id': prediction_log.id,
                    'filename': img_info['filename'],
                    'predicted_class': result['predicted_class'],
                    'confidence': result['confidence'],
                    'class_probabilities': result['class_probabilities'],
                    'processing_time': result['processing_time'],
                    'image_info': img_info
                })
            
            response_data = {
                'batch_size': len(images),
                'total_processing_time': total_processing_time,
                'average_processing_time': total_processing_time / len(images),
                'device': batch_results[0]['device'] if batch_results else 'unknown',
                'ml_app': ml_app.name,
                'results': results
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return Response({
                'error': f'Batch prediction failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def device_info(self, request, pk=None):
        """デバイス情報を取得"""
        ml_app = self.get_object()
        
        try:
            classifier = get_classifier(device_type=ml_app.device_type)
            device_info = classifier.get_device_info()
            
            return Response({
                'ml_app': ml_app.name,
                'configured_device': ml_app.device_type,
                'device_info': device_info
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Device info error: {e}")
            return Response({
                'error': f'Failed to get device info: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def benchmark(self, request, pk=None):
        """推論速度ベンチマーク"""
        ml_app = self.get_object()
        
        if ml_app.app_type != 'image_classification':
            return Response({
                'error': f'Benchmark not supported for {ml_app.app_type}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        iterations = request.data.get('iterations', 50)
        iterations = int(iterations)  # 文字列を整数に変換
        iterations = min(max(iterations, 10), 200)  # 10-200の範囲
        
        try:
            classifier = get_classifier(device_type=ml_app.device_type)
            benchmark_result = classifier.benchmark(num_iterations=iterations)
            
            return Response({
                'ml_app': ml_app.name,
                'benchmark': benchmark_result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Benchmark error: {e}")
            return Response({
                'error': f'Benchmark failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        processing_time = time.time() - start_time
        
        # ログ保存
        PredictionLog.objects.create(
            ml_app=ml_app,
            input_data=input_data,
            output_data=result,
            processing_time=processing_time
        )
        
        output_data = {
            'result': result,
            'processing_time': processing_time
        }
        
        output_serializer = PredictionOutputSerializer(output_data)
        return Response(output_serializer.data)
    
    def dummy_prediction(self, ml_app, input_data):
        """ダミー推論処理"""
        # 実際の実装では、ここで機械学習モデルを呼び出します
        return {
            'prediction': random.uniform(0, 1),
            'confidence': random.uniform(0.8, 1.0),
            'model': ml_app.name,
            'timestamp': timezone.now().isoformat()
        }

class PredictionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """推論ログの一覧・詳細取得"""
    queryset = PredictionLog.objects.all()
    serializer_class = PredictionLogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        ml_app_id = self.request.query_params.get('ml_app', None)
        if ml_app_id is not None:
            queryset = queryset.filter(ml_app_id=ml_app_id)
        return queryset
