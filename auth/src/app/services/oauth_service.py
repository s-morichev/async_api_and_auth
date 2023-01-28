import json
from uuid import UUID

from flask import current_app, url_for, redirect, request, jsonify
from flask_jwt_extended import set_refresh_cookies, set_access_cookies
from rauth import OAuth2Service

from app.db.database import AbstractSocialAccounts, AbstractUsers
from app.services import token_service, auth_service
from app.core.utils import generate_password

social_accounts: AbstractSocialAccounts
users: AbstractUsers


def login_by_social(social_name: str, social_user_id: str, user_name: str, email: str | None):
    """
        Осуществляет вход через соц сеть. Если аккаунта соц сети нет - создает его
        и привязывает по email к пользователю с таким же email
        Если пользователь с таким email не найден - создает такого пользователя, возвращает
        JSON {login, password}
        Если email от соцсети отсутствует - тогда создаем пользователя с email равным user_id
        и при входе настоятельно просим ввести email))) Или нет...

    """

    def add_new_user(email, user_name, social_name, social_user_id):
        current_app.logger.debug(f'add new user from social email:"{email}" '
                                 f'username:"{user_name}" social_net:"{social_name}" social_user_id:"{social_user_id}"')
        password = generate_password()
        user = users.add_user(email, password, user_name)
        new_user_data = {'login': user.login, 'password': password}
        social_accounts.add_social(user.id, social_user_id, social_name)
        return user, new_user_data

    user_id = social_accounts.user_by_social(social_id=social_user_id, social_name=social_name)
    device_name = request.headers.get("User-Agent")
    remote_ip = request.remote_addr
    new_user_data = {}
    user = None

    if user_id:
        user = users.user_by_id(user_id)
    else:
        # если есть почта
        if email:
            user = users.user_by_login(email)
            # и есть пользователь с такой почтой
            if user:
                # привязываем соц аккаунт к пользователю
                social_accounts.add_social(user.id, social_user_id, social_name)

        # если в результате пользователя так и нет - создаем его
        if not user:
            user, new_user_data = add_new_user(email, user_name, social_name, social_user_id)

    access_token, refresh_token = token_service.new_tokens(user, device_name)
    # ttl - time of session life
    ttl = token_service.get_refresh_token_expires()
    auth_service.new_session(user.id, device_name, remote_ip, ttl, social_net=social_name)

    if new_user_data:
        response = jsonify(new_user=new_user_data, access_token=access_token, refresh_token=refresh_token)
    else:
        response = jsonify(access_token=access_token, refresh_token=refresh_token)
    set_refresh_cookies(response, refresh_token)
    set_access_cookies(response, access_token)
    return response


def get_user_socials(user_id: UUID) -> list[dict]:
    socials = social_accounts.get_user_socials(user_id)
    result = [social.dict() for social in socials]
    return result


def del_user_social(user_id: UUID, social_id: UUID) -> list[dict]:
    socials = social_accounts.delete_user_social(user_id, social_id)
    result = [social.dict() for social in socials]
    return result


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
            #scope='login:email',
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
        email = str(info['default_email']).lower()
        # если нет имени - вернуть почту
        user_name = info.get('display_name', email)

        return user_id, user_name, email


class VKSignIn(OAuthSignIn):
    def __init__(self):
        super().__init__('vk')
        self.service = None

        self.service = OAuth2Service(
            name='vk',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.vk.com/authorize',
            access_token_url='https://oauth.vk.com/access_token',
            base_url='https://api.vk.com/method/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            # scope='email',
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
        email = str(raw_token.get('email', '')).lower()

        oauth_session = self.service.get_session(token=access_token)
        info = oauth_session.get('users.get', params={'v': '5.131'}).json()

        if 'response' not in info:
            return None, None, None

        response = info['response'][0]
        user_id = str(response['id'])
        user_name = f"{response['first_name']} {response['last_name']}"

        return user_id, user_name, email
