import requests
from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        provider = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        credentials = provider['credentials']
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

        self.provider_request_token_url = provider['request_token_url']
        self.provider_authorize_url = provider['authorize_url']
        self.provider_access_token_url = provider['access_token_url']
        self.provider_base_url = provider['base_url']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


def get_avatar_url(access_token, user_id):
    url = 'https://graph.facebook.com/{0}/picture'.format(user_id)
    response = requests.get(url, params={'type': 'square', 'access_token': access_token})
    return response.url


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url=self.provider_authorize_url,
            access_token_url=self.provider_access_token_url,
            base_url=self.provider_base_url
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()

        user_id = str(me.get('id'))
        social_id = 'facebook$' + user_id
        username = me.get('name')
        avatar_url = None

        access_token = oauth_session.access_token
        if access_token is not None:
            avatar_url = get_avatar_url(access_token, user_id)

        return social_id, username, avatar_url


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url=self.provider_request_token_url,
            authorize_url=self.provider_authorize_url,
            access_token_url=self.provider_access_token_url,
            base_url=self.provider_base_url
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(me.get('id'))
        username = me.get('name')
        avatar_url = me.get('profile_image_url').replace('_normal', '_bigger')
        return social_id, username, avatar_url
