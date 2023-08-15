from django.conf import settings

USER_SETTINGS = getattr(settings, 'PASSWORDLESS_AUTH', None)


DEFAULTS = {
    'PASSWORDLESS_AUTH_TYPES': ['EMAIL'],
    'PASSWORDLESS_AUTH_PREFIX': 'auth/',
    'PASSWORDLESS_VERIFY_PREFIX': 'auth/verify/',
    'PASSWORDLESS_TOKEN_EXPIRE_TIME': 15 * 60,
    'PASSWORDLESS_USER_EMAIL_FIELD_NAME': 'email',
    'PASSWORDLESS_USER_MOBILE_FIELD_NAME': 'mobile',
    'PASSWORDLESS_USER_MARK_EMAIL_VERIFIED': False,
    'PASSWORDLESS_USER_EMAIL_VERIFIED_FIELD_NAME': 'email_verified',
    'PASSWORDLESS_USER_MARK_MOBILE_VERIFIED': False,
    'PASSWORDLESS_USER_MOBILE_VERIFIED_FIELD_NAME': 'mobile_verified',
    'PASSWORDLESS_EMAIL_NOREPLY_ADDRESS': None,
    'PASSWORDLESS_EMAIL_SUBJECT': "Your Login Token",
    'PASSWORDLESS_EMAIL_PLAINTEXT_MESSAGE': "Enter this token to sign in: %s",
    'PASSWORDLESS_EMAIL_TOKEN_HTML_TEMPLATE_NAME': "passwordless_default_token_email.html",
    'PASSWORDLESS_MOBILE_NOREPLY_NUMBER': None,
    'PASSWORDLESS_MOBILE_MESSAGE': "Use this code to log in: %s",
    'PASSWORDLESS_REGISTER_NEW_USERS': True,
    'PASSWORDLESS_TEST_SUPPRESSION': False,
    'PASSWORDLESS_CONTEXT_PROCESSORS': [],
    'PASSWORDLESS_EMAIL_VERIFICATION_SUBJECT': "Your Verification Token",
    'PASSWORDLESS_EMAIL_VERIFICATION_PLAINTEXT_MESSAGE': "Enter this verification code: %s",
    'PASSWORDLESS_EMAIL_VERIFICATION_TOKEN_HTML_TEMPLATE_NAME': "passwordless_default_verification_token_email.html",
    'PASSWORDLESS_MOBILE_VERIFICATION_MESSAGE': "Enter this verification code: %s",
    'PASSWORDLESS_AUTO_SEND_VERIFICATION_TOKEN': False,
    'PASSWORDLESS_AUTH_TOKEN_CREATOR': 'ninja_passwordless.utils.create_authentication_token',
    'PASSWORDLESS_AUTH_TOKEN_SERIALIZER': 'ninja_passwordless.serializers.TokenResponseSerializer',
    'PASSWORDLESS_DEMO_USERS': {},
    'PASSWORDLESS_EMAIL_CALLBACK': 'ninja_passwordless.utils.send_email_with_callback_token',
    'PASSWORDLESS_SMS_CALLBACK': 'ninja_passwordless.utils.send_sms_with_callback_token',
    'PASSWORDLESS_TOKEN_GENERATION_ATTEMPTS': 3
}

# Retrieving settings or default values
for setting, default_value in DEFAULTS.items():
    globals()[setting] = getattr(USER_SETTINGS, setting, default_value)
