from django_eventstream.channelmanager import DefaultChannelManager

class NotificationsChannelManager(DefaultChannelManager):
    def can_read_channel(self, user, channel):
        # require auth for prefixed channels
        if user is None:
            return False
        return True
    
    def get_channels_for_request(self, request, view_kwargs):
        out = set()
        if request.user.is_authenticated:
            out.add(f"user:{request.user.id}")

        return out