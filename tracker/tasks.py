from celery import shared_task
from .models import SiteVisitTracker

import urllib.request
import json

@shared_task
def get_ip_location(ip):
    with urllib.request.urlopen(f"http://ip-api.com/json/{ip}") as url:
        data = url.read().decode()
        j = json.loads(data)
        
        try:
            location = f"{j['country']}:{j['regionName']}:{j['city']}"
        except KeyError:
            location = "something went wrong"
            
        try:
            record: SiteVisitTracker = SiteVisitTracker.objects.filter(ip=ip).first()
            record.location = location
            record.save()
        except SiteVisitTracker.DoesNotExist:
            pass

        return True