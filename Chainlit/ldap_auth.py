import ldap3
from ldap3.core.exceptions import LDAPBindError, LDAPInvalidCredentialsResult

class LDAPAuthenticator:
    def __init__(self, server_address, service_user, service_password):
        self.server = ldap3.Server(server_address)
        self.service_user = service_user
        self.service_password = service_password
        self.service_connection = None
        self.connect_service_account()

    def connect_service_account(self):
        try:
            self.service_connection = ldap3.Connection(
                self.server, user=self.service_user, password=self.service_password, auto_bind=True)
            print("Service account connected successfully")
        except LDAPBindError as e:
            print(f"Service account connection failed: {e}")

    def authenticate_ldap_user(self, user_dn, user_password):
        try:
            connection = ldap3.Connection(self.server, user=user_dn, password=user_password, auto_bind=True)
            print("User authentication successful")
            connection.unbind()
            return True
        except LDAPBindError as e:
            print(f"User authentication failed: {e}")
            return False
        except LDAPInvalidCredentialsResult as e:
            print(f"Invalid credentials: {e}")
            return False

    def get_user_dn(self, username):
        if not self.service_connection:
            self.connect_service_account()

        self.service_connection.search(
            search_base='dc=jbbl,dc=local',
            search_filter=f'(sAMAccountName={username})',
            attributes=['distinguishedName']
        )

        if self.service_connection.entries:
            user_dn = self.service_connection.entries[0].distinguishedName.value
            return user_dn
        else:
            print("User not found")
            return None

    def ldap_validate_user(self, username, password):
        user_dn = self.get_user_dn(username)
        if user_dn:
            return self.authenticate_ldap_user(user_dn, password)
        else:
            return False

ldap_authenticator = LDAPAuthenticator(
    server_address='jbbl.local',
    service_user='ai.chatbot@jbbl.local',
    service_password='Intelligence@B0t4'
)

def ldap_validate_user(username, password):
    return ldap_authenticator.ldap_validate_user(username, password)
