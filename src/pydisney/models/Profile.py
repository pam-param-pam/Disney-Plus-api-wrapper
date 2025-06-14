from .Language import Language
from .Rating import Rating
from ..Auth import Auth
from ..Config import APIConfig
from ..models.LanguagePreferences import LanguagePreferences


class Profile:
    def __init__(self, profile_id, name, kids_mode, is_default, av_id, av_user_selected):
        self.id = profile_id
        self.name = name
        self.kids_mode = kids_mode
        self.avatar = {"id": av_id, "user_selected": av_user_selected}
        self.is_default = is_default
        self.language_preferences = LanguagePreferences()

    def _get_action_grant(self) -> str:
        graphql_mutation = {
            "query": """
                    mutation authenticate($input: AuthenticateInput!) {
                      authenticate(authenticate: $input) {
                        actionGrant
                      }
                    }
                  """,
            "variables": {
                "input": {
                    "email": APIConfig.auth._email,
                    "password": APIConfig.auth._password,
                    "reasons": [
                        "UpdateProfileMaturityRating"
                    ]
                }
            },
            "operationName": "authenticate"
        }
        res = Auth.make_request("POST", "https://disney.api.edge.bamgrid.com/v1/public/graphql", data=graphql_mutation)
        return res["data"]["authenticate"]["actionGrant"]

    def set_profile_maturity_rating(self, rating: Rating) -> None:
        actionGrant = self._get_action_grant()
        graphql_mutation = {
            "query": """
            mutation updateProfileMaturityRatingWithActionGrant($input: UpdateProfileMaturityRatingWithActionGrantInput!) {
              updateProfileMaturityRatingWithActionGrant(updateProfileMaturityRatingWithActionGrant: $input) {
                accepted
              }
            }
          """,
            "variables": {
                "input": {
                    "actionGrant": actionGrant,
                    "contentMaturityRating": rating.value,
                    "profileId": self.id,
                    "ratingSystem": "DisneyPlusEMEA"
                }
            },
            "operationName": "updateProfileMaturityRatingWithActionGrant"
        }
        Auth.make_request("POST", "https://disney.api.edge.bamgrid.com/v1/public/graphql", data=graphql_mutation)

    def set_profile_language(self, language: Language):
        graphql_mutation = {
            "query": """
            mutation updateProfileAppLanguage($input: UpdateProfileAppLanguageInput!) {
                updateProfileAppLanguage(updateProfileAppLanguage: $input) {
                    accepted
                }
            }
            """,
            "variables": {
                "input": {
                    "appLanguage": language.value,
                    "profileId": self.id
                }
            },
            "operationName": "updateProfileAppLanguage"
        }
        Auth.make_request("POST", "https://disney.api.edge.bamgrid.com/v1/public/graphql", data=graphql_mutation)

    def __str__(self):
        return f"Profile({self.name})"

    def __repr__(self):
        return self.name


