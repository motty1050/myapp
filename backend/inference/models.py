from django.db import models

class MLApp(models.Model):
    """機械学習アプリのモデル"""
    name = models.CharField(max_length=100, verbose_name="アプリ名")
    description = models.TextField(verbose_name="説明")
    endpoint = models.CharField(max_length=200, verbose_name="推論エンドポイント", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MLアプリ"
        verbose_name_plural = "MLアプリ"

    def __str__(self):
        return self.name

class PredictionLog(models.Model):
    """推論ログのモデル"""
    ml_app = models.ForeignKey(MLApp, on_delete=models.CASCADE, verbose_name="MLアプリ")
    input_data = models.JSONField(verbose_name="入力データ")
    output_data = models.JSONField(verbose_name="出力データ")
    processing_time = models.FloatField(verbose_name="処理時間（秒）", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "推論ログ"
        verbose_name_plural = "推論ログ"
        ordering = ['-created_at']
