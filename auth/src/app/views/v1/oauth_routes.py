from http import HTTPStatus

from flask import Blueprint, redirect, flash, url_for
from app.services.oauth_service import OAuthSignIn
from app.core.utils import error
oauth_bp = Blueprint("oauth", __name__)


@oauth_bp.route('/callback/<provider>')
def oauth_callback(provider):
    oauth = OAuthSignIn.get_provider(provider)
    if not oauth:
        error('Auth provider not found', HTTPStatus.NOT_FOUND)

    social_id, username, email = oauth.callback()
    if social_id is None:
        error('Authentication failed', HTTPStatus.UNAUTHORIZED)
        #return redirect(url_for('default.get_index'))

    print(social_id, username, email)
    return redirect(url_for('default.get_index'))


@oauth_bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    if not oauth:
        error('Auth provider not found', HTTPStatus.NOT_FOUND)
    return oauth.authorize()

