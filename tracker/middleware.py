from .models import SiteVisitTracker, SiteVisitTrackerVisitedPath

from django.utils import timezone
from django.conf import settings

import re

def site_visits_logger(get_response):

    def middleware(request):

        response = get_response(request)
        ignore_paths = ["/favicon.ico",
                        "/admin/",
                        "/rosetta/",
                        settings.MEDIA_URL,
                        settings.STATIC_URL]
        if re.search(r"/[a-z]{2}/", request.path[0:255], re.IGNORECASE): # remove
            path_str = request.path[3:259]
        else:
            path_str = request.path[0:255]
        
        for p in ignore_paths: # ignore icon path, admin related path and static files paths.
            if path_str.startswith(p):
                return response
        try:
            record = SiteVisitTracker.objects.filter(ip=request.META["REMOTE_ADDR"]).first()
            if record:
                
                path: SiteVisitTrackerVisitedPath = record.visited_paths.filter(path=path_str).first()
                if path:
                    path.updated_at = timezone.now()
                else:
                    path = record.visited_paths.create(path=path_str)

                path.save()
        except Exception as e:
            print(f"[Error] exeption \"{e}\" happened while trying to log site visits.")
        return response

    return middleware