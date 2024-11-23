from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):

    oidc_claim_scope = OAuth2Validator.oidc_claim_scope
    oidc_claim_scope.update({"permissions": "permissions"})

    def get_additional_claims(self):
        return {
            "id": lambda request: str(request.user.id),
            "key": lambda request: str(request.user.key),  # Assuming 'key' is the same as 'id'
            "email": lambda request: request.user.email,
            "name": lambda request: request.user.get_full_name(),
            "type": lambda request: request.user.type,
        }
    
    def get_userinfo_claims(self, request):
        claims = super().get_userinfo_claims(request)
        additional_claims = {
            "id": str(request.user.id),
            "key": str(request.user.key),  # Assuming 'key' is the same as 'id'
            "username": request.user.username,
            "email": request.user.email,
            "name": request.user.get_full_name(),
            "image": {
                "url": request.user.image.get_https_url(),
                "blurUrl": request.user.image.get_blur_url()
            } if hasattr(request.user, 'image') else None,
            "type": request.user.type,
            "vendor": {
                "key": request.user.vendor.key,
                "name": request.user.vendor.name,
                "image": {
                    "url": request.user.vendor.image.get_https_url(),
                    "blurUrl": request.user.vendor.image.get_blur_url() 
                } if hasattr(request.user.vendor, 'image') else None
            } if hasattr(request.user, 'vendor') else None,
        }
        claims.update(additional_claims)
        return claims