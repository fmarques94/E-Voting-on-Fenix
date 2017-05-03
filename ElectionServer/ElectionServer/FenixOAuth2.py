from social_core.backends.oauth import BaseOAuth2

class FenixOAuth2(BaseOAuth2):
    """Fenix OAuth authentication backend"""

    name="fenix"
    AUTHORIZATION_URL = 'https://fenix.tecnico.ulisboa.pt/login/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://fenix.tecnico.ulisboa.pt/login/oauth/access_token'
    SCOPE_SEPARATOR = ','

     def get_user_details(self, response):
        """Return user details from Fenix account"""
        return {'username': response.get('login'),
                'email': response.get('email') or '',
                'first_name': response.get('name')}

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person' + urlencode({
            'access_token': access_token
        })
        return self.get_json(url)
