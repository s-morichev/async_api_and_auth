import json

from flask import current_app, url_for, redirect, request
from rauth import OAuth2Service


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        resp = url_for('auth.auth_v1.oauth.oauth_callback', provider=self.provider_name,
                       _external=True)
        print(resp)
        return resp

    @classmethod
    def get_provider(cls, provider_name: str):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers.get(provider_name)


class YandexSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('yandex')
        self.service = OAuth2Service(
            name='yandex',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.yandex.ru/authorize',
            access_token_url='https://oauth.yandex.ru/token',
            base_url='https://oauth.yandex.ru'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            scope='login:email',
            force_confirm=1,
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None

        oauth_session = self.service.get_auth_session(data={'code': request.args['code'],
                                                            'grant_type': 'authorization_code'}, decoder=decode_json)

        info = oauth_session.get('https://login.yandex.ru/info', params={'format': 'json'}).json()

        user_id = info['id']
        user_name = info['display_name']
        email = info['default_email']

        return user_id, user_name, email


class VKSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('vk')
        self.service = None

        self.service = OAuth2Service(
            name='yandex',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.vk.com/authorize',
            access_token_url='https://oauth.vk.com/access_token',
            base_url='https://api.vk.com/method/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            scope='email',
            display='page',
            revoke=1,
            redirect_uri=self.get_callback_url()))

    def callback(self):
        def decode_json(payload):
            print(payload)
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None

        raw_token = self.service.get_raw_access_token(data={'code': request.args['code'],
                                                            'redirect_uri': self.get_callback_url()}).json()

        access_token = raw_token.get('access_token')
        if not access_token:
            return None, None, None

        # VK can return email if exists
        email = raw_token.get('email')

        oauth_session = self.service.get_session(token=access_token)
        info = oauth_session.get('users.get', params={'v': '5.131'}).json()

        if 'response' not in info:
            return None, None, None

        response = info['response'][0]
        user_id = response['id']
        user_name = f"{response['first_name']} {response['last_name']}"

        return user_id, user_name, email
