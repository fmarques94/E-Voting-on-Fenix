from social_core.backends.oauth import BaseOAuth2
import urllib

class FenixOAuth2(BaseOAuth2):
    """Fenix OAuth authentication backend"""

    name='fenix'
    AUTHORIZATION_URL = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog'
    ACCESS_TOKEN_URL = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'
    REDIRECT_STATE = False
    STATE_PARAMETER = False
    ACCESS_TOKEN_METHOD = 'POST'
    SCOPE_SEPARATOR = ','

    def get_user_details(self, response):
        """Return user details from Fenix account"""
        return {'username': response.get('username'),
                'email': response.get('email'),
                'full_name': response.get('name')}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        response = self.get_json('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person',
                                 params={'access_token': access_token})
        return response
