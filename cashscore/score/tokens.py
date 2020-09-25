from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, application, timestamp):
        return (
            str(application.id) +
            str(timestamp) +
            str(application.applicant_connected_to_plaid) # using applicant_connected_to_plaid will invalidate it once the applicant completes their part
        )


application_token = TokenGenerator()
