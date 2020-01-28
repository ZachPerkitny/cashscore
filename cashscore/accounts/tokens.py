from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.id) + 
            str(timestamp) +
            str(user.is_active) # using is_active will invalidate it once user is activated
        )


account_activation_token = TokenGenerator()
