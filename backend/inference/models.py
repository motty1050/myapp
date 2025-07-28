from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class MLApp(models.Model):
    """機械学習アプリのモデル"""
    
    # アプリタイプの選択肢
    APP_TYPES = [
        ('image_classification', '画像分類'),
        ('object_detection', '物体検知'),
        ('text_classification', 'テキスト分類'),
        ('sentiment_analysis', '感情分析'),
    ]
    
    # 推論デバイスの選択肢
    DEVICE_TYPES = [
        ('auto', '自動選択'),
        ('cuda', 'CUDA (GPU)'),
        ('cpu', 'CPU'),
        ('mps', 'MPS (Apple Silicon)')
    ]
    
    name = models.CharField(max_length=100, verbose_name="アプリ名")
    description = models.TextField(verbose_name="説明")
    app_type = models.CharField(max_length=50, choices=APP_TYPES, default='image_classification', verbose_name="アプリタイプ")
    endpoint = models.CharField(max_length=200, verbose_name="推論エンドポイント", null=True, blank=True)
    model_file_path = models.CharField(max_length=300, verbose_name="モデルファイルパス", null=True, blank=True)
    classes = models.JSONField(default=list, verbose_name="分類クラス一覧")  # ['cat', 'dog']
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='auto', verbose_name="推論デバイス")
    batch_size = models.PositiveIntegerField(default=1, verbose_name="バッチサイズ")
    use_mixed_precision = models.BooleanField(default=False, verbose_name="混合精度使用")
    model_optimization = models.JSONField(default=dict, verbose_name="モデル最適化設定")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MLアプリ"
        verbose_name_plural = "MLアプリ"

    def __str__(self):
        return self.name
    
    def get_device_info(self):
        """使用可能なデバイス情報を取得"""
        import torch
        if self.device_type == 'auto':
            if torch.cuda.is_available():
                return {
                    'device': 'cuda',
                    'name': torch.cuda.get_device_name(0),
                    'memory': f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB"
                }
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return {'device': 'mps', 'name': 'Apple Silicon GPU'}
            else:
                return {'device': 'cpu', 'name': 'CPU'}
        return {'device': self.device_type}
    
    def get_optimal_batch_size(self):
        """デバイスに応じた最適なバッチサイズを取得"""
        device_info = self.get_device_info()
        if device_info['device'] == 'cuda':
            # GPU VRAMに応じてバッチサイズを調整
            return min(self.batch_size * 4, 32)
        return self.batch_size

class PredictionLog(models.Model):
    """推論ログのモデル"""
    ml_app = models.ForeignKey(MLApp, on_delete=models.CASCADE, verbose_name="MLアプリ")
    input_data = models.JSONField(verbose_name="入力データ")
    output_data = models.JSONField(verbose_name="出力データ")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], 
        verbose_name="信頼度", 
        null=True, 
        blank=True
    )
    predicted_class = models.CharField(max_length=100, verbose_name="予測クラス", null=True, blank=True)
    processing_time = models.FloatField(verbose_name="処理時間（秒）", null=True, blank=True)
    user_feedback = models.CharField(
        max_length=20, 
        choices=[('correct', '正解'), ('incorrect', '不正解')], 
        verbose_name="ユーザーフィードバック", 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "推論ログ"
        verbose_name_plural = "推論ログ"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.ml_app.name} - {self.predicted_class} ({self.confidence_score:.2f})"

class ImageUpload(models.Model):
    """画像アップロード管理"""
    prediction_log = models.ForeignKey(PredictionLog, on_delete=models.CASCADE, verbose_name="推論ログ")
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/', verbose_name="アップロード画像")
    original_filename = models.CharField(max_length=255, verbose_name="元ファイル名")
    file_size = models.PositiveIntegerField(verbose_name="ファイルサイズ（バイト）")
    image_width = models.PositiveIntegerField(verbose_name="画像幅", null=True, blank=True)
    image_height = models.PositiveIntegerField(verbose_name="画像高さ", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "画像アップロード"
        verbose_name_plural = "画像アップロード"
