import time
import random
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import MLApp, PredictionLog
from .serializers import MLAppSerializer, PredictionInputSerializer, PredictionOutputSerializer, PredictionLogSerializer

class MLAppViewSet(viewsets.ReadOnlyModelViewSet):
    """ML アプリの一覧・詳細取得"""
    queryset = MLApp.objects.filter(is_active=True)
    serializer_class = MLAppSerializer

    @action(detail=True, methods=['post'])
    def predict(self, request, pk=None):
        """特定のMLアプリで推論を実行"""
        ml_app = self.get_object()
        
        # 入力データの検証
        input_serializer = PredictionInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        input_data = input_serializer.validated_data['data']
        
        # 推論実行（ここではダミー実装）
        start_time = time.time()
        result = self.dummy_prediction(ml_app, input_data)
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
