from Auth import Auth
from Config import APIConfig


class Avatar:
    def __init__(self, avatar_id, user_selected):
        self.id = avatar_id
        self.user_selected = user_selected

        self._name = None
        self._image = None

    @property
    def image(self):
        if not self._image:
            self._get_more_data()
        return self._image

    @property
    def name(self):
        if not self._name:
            self._get_more_data()
        return self._name

    def _get_more_data(self):
        res = Auth.make_get_request(
            f"https://disney.content.edge.bamgrid.com/svc/content/Avatars/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/avatarIds/{self.id}")
        res_json = res.json()["data"]["Avatars"]["avatars"][0]
        self._image = res_json["image"]["tile"]["1.00"]["avatar"]["default"]["url"]

        self._name = res_json["text"]["title"]["full"]["avatar"]["default"]["content"]

    def __str__(self):
        return f"Avatar({self.id})"

    def __repr__(self):
        return f"Avatar({self.id})"


"https://prod-ripcut-delivery.disney-plus.net/v1/variant/disney/E6BDC816F7F0F83E882316B59622B1041A7DAB53FDE62AA920BCD7C1230AFCD2"
