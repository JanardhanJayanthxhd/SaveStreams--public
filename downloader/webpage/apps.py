from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
from shutil import rmtree


CLEAR_DB_INTERVAL_MINS = 15
CLEAR_KEYS_INTERVAL_SECS = 30

class WebpageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webpage'
        

    def ready(self):
        self.deleter()

    def deleter(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            self.clear_dir_job, 'interval', minutes=CLEAR_DB_INTERVAL_MINS, 
            misfire_grace_time=30
        )
        scheduler.add_job(
            self.clear_expired_keys, 'interval', seconds=CLEAR_KEYS_INTERVAL_SECS, 
            misfire_grace_time=30
        )
        scheduler.start()

    @staticmethod
    def clear_dir_job():
        """
        Deletes the contents of a file if the logged(VideoLog db) time expires.
        """
        from .models import VideoLog
        all_logs = VideoLog.object.all()

        for log in all_logs:
            curr_timestamp = datetime.now().replace(tzinfo=None)
            log_time = log.expires_at.replace(tzinfo=None)
            
            print(f'current_time: {curr_timestamp}, logged time: {log_time}')

            if log_time < curr_timestamp:
                print(f'File {log.file_name} has expired {log.expires_at}')
                if log.file_type == 'directory':
                    rmtree(log.file_path)
                else:
                    os.remove(os.path.join(log.file_path, log.file_name))
                log.delete()

    @staticmethod
    def clear_expired_keys():
        """
        Deletes spotify key after it expires (uses KeyLog table) and adds a newone.
        """
        from .models import KeyLog
        from webpage.utility import get_spotify_token
        all_keys = KeyLog.object.all()
        key_length = len(all_keys)
        print(f'All keys:{all_keys} \nkey len {key_length} {type(key_length)}')

        for key in all_keys:
            curr_timestamp = datetime.now().replace(tzinfo=None)
            if key.expires_at.replace(tzinfo=None) < curr_timestamp:
                print(f'Key {key.api_token} has expired {key.expires_at}')
                key.delete()
                key_length -= 1

        if key_length == 0:
            get_spotify_token(add_new=True)

