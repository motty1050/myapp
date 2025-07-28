from rest_framework import serializers
from .models import MLApp, PredictionLog

class MLAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLApp
        fields = [
            'id', 'name', 'description', 'app_type', 'device_type',
            'classes', 'batch_size', 'use_mixed_precision', 
            'model_optimization', 'is_active', 'created_at'
        ]

class PredictionInputSerializer(serializers.Serializer):
    """推論入力データのシリアライザ"""
    data = serializers.JSONField()

class PredictionOutputSerializer(serializers.Serializer):
    """推論出力データのシリアライザ"""
    result = serializers.JSONField()
    processing_time = serializers.FloatField(required=False)
    
class PredictionLogSerializer(serializers.ModelSerializer):
    ml_app_name = serializers.CharField(source='ml_app.name', read_only=True)
    
    class Meta:
        model = PredictionLog
        fields = ['id', 'ml_app', 'ml_app_name', 'input_data', 'output_data', 'processing_time', 'created_at']
