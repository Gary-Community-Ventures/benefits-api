from .models import Screen
from programs.models import Referrer
from .serializers import ScreenSerializer
import requests


class Hook:
    def __init__(self, hook: Referrer):
        self.hook = hook
        self.functions = [func.name for func in hook.webhook_functions.all()]

    def send(self, screen: Screen, results: dict):
        if screen.completed:
            return
        request_data = {"external_id": screen.external_id}
        if "send_screen" in self.functions:
            key, value = self.screen_data(screen)
            request_data[key] = value
        if "send_results" in self.functions:
            key, value = self.send_eligibility(results)
            request_data[key] = value

        try:
            requests.post(self.hook.webhook_url, json=request_data)
        except requests.exceptions.RequestException:
            # TODO: add logging
            pass

    def screen_data(self, screen: Screen):
        screen_dict = ScreenSerializer(screen).data
        return "screen", screen_dict

    def send_eligibility(self, results: dict):
        return "eligibility", results


def eligibility_hooks():
    hooks: dict[str, Hook] = {}

    for hook in Referrer.objects.all():
        hooks[hook.referrer_code] = Hook(hook)

    return hooks
