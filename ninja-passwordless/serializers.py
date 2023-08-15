import logging
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from pydantic import BaseModel, EmailStr, constr, ValidationError
from typing import Optional
from ninjapasswordless.models import CallbackToken
from ninjapasswordless.settings import api_settings
from ninjapasswordless.utils import verify_user_alias, validate_token_age

logger = logging.getLogger(__name__)
User = get_user_model()


class TokenField(BaseModel):
    token: constr(min_length=6, max_length=6)


class AbstractBaseAliasAuthenticationModel(BaseModel):
    user: Optional[User]

    class Config:
        arbitrary_types_allowed = True

    @property
    def alias_type(self):
        # The alias type, either email or mobile
        raise NotImplementedError

    def validate_alias(self):
        alias = getattr(self, self.alias_type, None)
        if not alias:
            raise ValueError(f"Missing {self.alias_type}")

        if api_settings.PASSWORDLESS_REGISTER_NEW_USERS:
            user, _ = User.objects.get_or_create(**{self.alias_type: alias})
            if not user.has_usable_password():
                user.set_unusable_password()
                user.save()
        else:
            try:
                user = User.objects.get(**{self.alias_type+'__iexact': alias})
            except User.DoesNotExist:
                raise ValueError(_('No account is associated with this alias.'))

        if not user.is_active:
            raise ValueError(_('User account is disabled.'))

        return user


class EmailAuthModel(AbstractBaseAliasAuthenticationModel):
    alias_type = 'email'
    email: EmailStr


class MobileAuthModel(AbstractBaseAliasAuthenticationModel):
    alias_type = 'mobile'
    mobile: constr(regex=r'^\+[1-9]\d{1,14}$')


class AbstractBaseAliasVerificationModel(BaseModel):
    user: Optional[User]

    class Config:
        arbitrary_types_allowed = True

    @property
    def alias_type(self):
        raise NotImplementedError

    def validate_alias(self, request):
        user = request.user
        if not user.is_active:
            raise ValueError(_('User account is disabled.'))
        if hasattr(user, self.alias_type):
            return user
        else:
            raise ValueError(f"This user doesn't have an {self.alias_type}.")


class EmailVerificationModel(AbstractBaseAliasVerificationModel):
    alias_type = 'email'


class MobileVerificationModel(AbstractBaseAliasVerificationModel):
    alias_type = 'mobile'


def token_age_validator(value: str):
    if not validate_token_age(value):
        raise ValueError("The token you entered isn't valid.")
    return value


class AbstractBaseCallbackTokenModel(BaseModel):
    email: Optional[EmailStr]
    mobile: Optional[constr(regex=r'^\+[1-9]\d{1,14}$')]
    token: TokenField

    def validate_alias(self):
        if self.email and self.mobile:
            raise ValueError("Cannot provide both email and mobile.")

        if not self.email and not self.mobile:
            raise ValueError("Either email or mobile must be provided.")

        return 'email' if self.email else 'mobile', self.email or self.mobile


class CallbackTokenAuthModel(AbstractBaseCallbackTokenModel):

    def validate(self):
        alias_type, alias = self.validate_alias()
        try:
            user = User.objects.get(**{alias_type+'__iexact': alias})
            token = CallbackToken.objects.get(user=user, key=self.token.token, type=CallbackToken.TOKEN_TYPE_AUTH, is_active=True)

            if token.user != user:
                raise ValueError(_('Invalid Token'))

            if api_settings.PASSWORDLESS_USER_MARK_EMAIL_VERIFIED or api_settings.PASSWORDLESS_USER_MARK_MOBILE_VERIFIED:
                success = verify_user_alias(user, token)
                if not success:
                    raise ValueError(_('Error validating user alias.'))

            return user

        except (CallbackToken.DoesNotExist, User.DoesNotExist):
            raise ValueError(_('Invalid alias parameters provided.'))


class CallbackTokenVerificationModel(AbstractBaseCallbackTokenModel):

    def validate(self, user_id):
        alias_type, alias = self.validate_alias()
        try:
            user = User.objects.get(id=user_id, **{alias_type+'__iexact': alias})
            token = CallbackToken.objects.get(user=user, key=self.token.token, type=CallbackToken.TOKEN_TYPE_VERIFY, is_active=True)

            if token.user != user:
                raise ValueError(_('This token is invalid. Try again later.'))

            success = verify_user_alias(user, token)
            if not success:
                logger.debug("ninjapasswordless: Error verifying alias.")

            return user

        except (CallbackToken.DoesNotExist, User.DoesNotExist):
            raise ValueError(_('We could not verify this alias.'))


class TokenResponseModel(BaseModel):
    token: str
