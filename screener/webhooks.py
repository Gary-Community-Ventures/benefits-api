from .models import Screen, WebHook
from .serializers import ScreenSerializer
import requests


class Hook():
    def __init__(self, hook: WebHook):
        self.hook = hook
        self.functions = [func.name for func in hook.functions.all()]

    def send(self, screen: Screen, results: dict):
        if screen.completed:
            return
        request_data = {'external_id': screen.external_id}
        if 'send_screen' in self.functions:
            key, value = self.screen_data(screen)
            request_data[key] = value
        if 'send_results' in self.functions:
            key, value = self.send_eligibility(results)
            request_data[key] = value

        try:
            requests.post(self.hook.url, json=request_data)
        except requests.exceptions.RequestException:
            # TODO: add logging
            pass

    def screen_data(self, screen: Screen):
        screen_dict = ScreenSerializer(screen).data
        return 'screen', screen_dict

    def send_eligibility(self, results: dict):
        return 'eligibility', results


eligibility_hooks: dict[str, Hook] = {}

for hook in WebHook.objects.all():
    eligibility_hooks[hook.referrer_code] = Hook(hook)
