class Account:
    def __init__(self, account_id, email, is_email_verified, country, created_at):
        self.id = account_id
        self.email = email
        self.is_email_verified = is_email_verified
        self.country = country
        self.created_at = created_at

    def __str__(self):
        return f"Account[Email={self.email}, Id={self.id}, Country={self.country}, Created_at={self.created_at}"

    def __repr__(self):
        return self.id
