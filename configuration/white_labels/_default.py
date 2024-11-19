from .base import ConfigurationData
from screener.models import WhiteLabel


class DefaultConfiguarationData(ConfigurationData):
    is_default = True

    @classmethod
    def get_white_label(self) -> WhiteLabel:
        return WhiteLabel.objects.get(code="_default")

    referrer_data = {
        "theme": {"default": "default"},
        "logoSource": {"default": ""},
        "logoAlt": {
            "default": {"id": "referrerHook.logoAlts.default", "defaultMessage": "MyFriendBen home page button"}
        },
        "logoFooterSource": {"default": "MFB_Logo"},
        "logoFooterAlt": {"default": {"id": "footer.logo.alt", "defaultMessage": "MFB Logo"}},
        "logoClass": {"default": "logo"},
        "twoOneOneLink": {
            "default": 'https://www.211colorado.org/?utm_source=myfriendben&utm_medium=inlink&utm_campaign=organic&utm_id="211mfb"'
        },
        "shareLink": {"default": "https://screener.myfriendben.org"},
    }

    footer_data = {
        "address_one": "1705 17th St.",
        "address_two": "Suite 200",
        "city": "Denver",
        "state": "CO",
        "zip_code": "80202",
        "email": "myfriendben@garycommunity.org",
        "privacy_policy_link": "https://co.myfriendben.org/privacy-policy/",
    }

    language_options = {
        "en-us": "English",
        "es": "Español",
        "vi": "Tiếng Việt",
        "fr": "Français",
        "am": "አማርኛ",
        "so": "Soomaali",
        "ru": "Русский",
        "ne": "नेपाली",
        "my": "မြန်မာဘာသာစကား",
        "zh": "中文",
        "ar": "عربي",
    }

    feedback_links = {
        "email": "mailto: myfriendben@garycommunity.org",
        "survey": "https://docs.google.com/forms/d/e/1FAIpQLSdnfqjvlVSBQkJuUMvhEDUp-t6oD-8tPQi67uRG2iNetXmSfA/viewform?usp=sf_link",
    }
