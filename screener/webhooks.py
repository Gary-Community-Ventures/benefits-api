from .models import Screen
import requests


def ccmcn_webhook(screen: Screen, results: dict):
    if screen.completed:
        return
    url = 'http://localhost:8080/'
    try:
        requests.post(url, json=results)
    except requests.exceptions.RequestException:
        # what to do on error?
        pass


eligibility_hooks = {
    'ccmcn': ccmcn_webhook
}
