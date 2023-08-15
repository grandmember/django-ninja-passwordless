import logging
from django.utils.module_loading import import_string
from ninja import Router
from typing import Any
from http import HTTPStatus
from ninjapasswordless.models import CallbackToken
from ninjapasswordless.settings import api_settings
from ninjapasswordless.serializers import (
    EmailAuthModel,
    MobileAuthModel,
    CallbackTokenAuthModel,
    CallbackTokenVerificationModel,
    EmailVerificationModel,
    MobileVerificationModel,
    TokenResponseModel
)
from ninjapasswordless.services import TokenService
from ninjapasswordless.settings import api_settings

logger = logging.getLogger(__name__)

router = Router()

def abstract_obtain_callback_token(request: Any, alias_model: Any, alias_type: str, token_type: str, success_response: str, failure_response: str, **kwargs):
    if alias_type.upper() not in api_settings.PASSWORDLESS_AUTH_TYPES:
        # Only allow auth types allowed in settings.
        return HTTPStatus.NOT_FOUND

    if alias_model:
        user = alias_model.user

        # Create and send callback token
        success = TokenService.send_token(user, alias_type, token_type, **kwargs)
        if success:
            return {'detail': success_response}
        else:
            return {'detail': failure_response}, HTTPStatus.BAD_REQUEST

    else:
        return {'detail': 'Bad Request'}, HTTPStatus.BAD_REQUEST


@router.post(api_settings.PASSWORDLESS_AUTH_PREFIX + 'email/', url_name='auth_email')
def obtain_email_callback_token(request, email_auth: EmailAuthModel):
    message_payload = {
        'email_subject': api_settings.PASSWORDLESS_EMAIL_SUBJECT,
        'email_plaintext': api_settings.PASSWORDLESS_EMAIL_PLAINTEXT_MESSAGE,
        'email_html': api_settings.PASSWORDLESS_EMAIL_TOKEN_HTML_TEMPLATE_NAME
    }
    return abstract_obtain_callback_token(request, email_auth, 'email', CallbackToken.TOKEN_TYPE_AUTH,
                                          "A login token has been sent to your email.",
                                          "Unable to email you a login code. Try again later.", **message_payload)


@router.post(api_settings.PASSWORDLESS_AUTH_PREFIX + 'mobile/', url_name='auth_mobile')
def obtain_mobile_callback_token(request, mobile_auth: MobileAuthModel):
    return abstract_obtain_callback_token(request, mobile_auth, 'mobile', CallbackToken.TOKEN_TYPE_AUTH,
                                          "We texted you a login code.",
                                          "Unable to send you a login code. Try again later.",
                                          mobile_message=api_settings.PASSWORDLESS_MOBILE_MESSAGE)


@router.post(api_settings.PASSWORDLESS_AUTH_PREFIX + 'token/', url_name='auth_token')
def obtain_auth_token_from_callback_token(request, callback_token_auth: CallbackTokenAuthModel):
    callback_token = callback_token_auth.callback_token
    user = callback_token.user
    token = TokenService.create_token_for_user(user)
    return TokenResponseModel(token.key)


@router.post(api_settings.PASSWORDLESS_VERIFY_PREFIX + 'email/', url_name='verify_email')
def verify_email_callback_token(request, email_verification: EmailVerificationModel):
    return abstract_obtain_callback_token(request, email_verification, 'email', CallbackToken.TOKEN_TYPE_VERIFY,
                                          "A verification token has been sent to your email.",
                                          "Unable to email you a verification code. Try again later.",
                                          email_subject=api_settings.PASSWORDLESS_EMAIL_VERIFICATION_SUBJECT,
                                          email_plaintext=api_settings.PASSWORDLESS_EMAIL_VERIFICATION_PLAINTEXT_MESSAGE,
                                          email_html=api_settings.PASSWORDLESS_EMAIL_VERIFICATION_TOKEN_HTML_TEMPLATE_NAME)


@router.post(api_settings.PASSWORDLESS_VERIFY_PREFIX + 'mobile/', url_name='verify_mobile')
def verify_mobile_callback_token(request, mobile_verification: MobileVerificationModel):
    return abstract_obtain_callback_token(request, mobile_verification, 'mobile', CallbackToken.TOKEN_TYPE_VERIFY,
                                          "We texted you a verification code.",
                                          "Unable to send you a verification code. Try again later.",
                                          mobile_message=api_settings.PASSWORDLESS_MOBILE_MESSAGE)

@router.post(api_settings.PASSWORDLESS_VERIFY_PREFIX + 'token/', url_name='verify_token')
def verify_alias_from_callback_token(request, callback_token_verification: CallbackTokenVerificationModel):
    callback_token = callback_token_verification.callback_token
    user = callback_token.user
    token = TokenService.create_token_for_user(user)
    return TokenResponseModel(token.key)
