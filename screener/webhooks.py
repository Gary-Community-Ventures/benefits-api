from .models import Screen
from programs.models import Referrer
from .serializers import ScreenSerializer
from sentry_sdk import capture_exception, capture_message
from typing import Optional
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
            res = requests.post(self.hook.webhook_url, json=request_data)
            if res.status_code != 200:
                capture_message(f"{res.text}", level="error")
        except requests.exceptions.RequestException as e:
            capture_exception(e)

    def screen_data(self, screen: Screen):
        screen_dict = ScreenSerializer(screen).data
        return "screen", screen_dict

    def send_eligibility(self, results: dict):
        return "eligibility", results


def get_web_hook(screen: Screen) -> Optional[Hook]:
    if screen.referrer_code is None:
        return None

    try:
        referrer = Referrer.objects.get(white_label=screen.white_label, referrer_code=screen.referrer_code)
    except Referrer.DoesNotExist:
        return None

    return Hook(referrer)
