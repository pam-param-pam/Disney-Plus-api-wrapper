class Account:
    def __init__(self, account_id, email, is_email_verified, country, created_at):
        self.id = account_id
        self.email = email
        self.is_email_verified = is_email_verified
        self.country = country
        self.created_at = created_at
