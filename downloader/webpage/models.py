from django.db import models

class VideoLog(models.Model):
    """
    VideoLog : Used to log all the files (video or directories) that are downloaded on the server
    """
    object = models.Manager()

    file_path = models.CharField(max_length=600, null=False, blank=False)
    file_name = models.CharField(max_length=200, null=True, blank=True)
    file_type = models.CharField(max_length=10, default='audio')
    file_metadata = models.CharField(max_length=100, null=False, default='yt_audio')
    file_audio_quality = models.CharField(max_length=5, null=False, blank=False, default="192")
    expires_at = models.DateTimeField(null=True, blank=True)
    batch_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.file_metadata

class KeyLog(models.Model):
    """
    KeyLog : Tracks the spotify api key (which expires after an hour)
    """
    object = models.Manager()

    api_token = models.CharField(max_length=400)
    expires_at = models.DateTimeField(null=True, blank=True)
