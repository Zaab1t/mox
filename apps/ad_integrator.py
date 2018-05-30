# encoding: utf-8
""" POC of using pywinrm for AD management """
import winrm


class AdIntegrator(object):
    def __init__(self):
        self.session = winrm.Session('https://192.168.1.234:5986/wsman',
                                     transport='ntlm',
                                     server_cert_validation='ignore',
                                     auth=('AD\Administrator', ''))
        self.dc = 'dc=ad,dc=magenta-aps,dc=dk'

    def test_connection(self, debug=False):
        """ Test that the winrm connection works
        :param debug: If true more output will be written to terminal
        :return: Return true if connection succeeded
        """
        r = self.session.run_cmd('ipconfig', ['/all'])
        if debug:
            print(r.status_code)
            print(r.std_out)
            print(r.std_err)
        return r.status_code == 0

    def create_password(self, user=None):
        """ Create a password for a user.
        Not implemented, returns hard-coded password
        :param user: The user that needs the password
        :return: A password
        """
        return 'v30ccMNVEIC'.encode('ascii')

    def create_user(self, name, ou, debug=False):
        """ Create an AD user
        :param name: Name of the new user
        :param ou: AD Organisational Unit for the new user
        :param debug: If True, more output will be written to terminal
        :return: Success if creation succeeded
        """
        password = self.create_password()
        username = name[0] + name[-5:]
        username = username.replace(' ', '')
        username = username.lower()
        path = '"OU=' + ou + ',' + self.dc + '"'
        ps_script = ('New-ADUser -Name "{0}" -DisplayName "{0}" ' +
                     ' -SamAccountName "{1}" -Enable 1 ' +
                     ' -Path ' + path +
                     ' -AccountPassword (ConvertTo-SecureString {2} ' +
                     ' -AsPlainText -Force)').format(name, username, password)
        r = self.session.run_ps(ps_script.decode("utf8"))
        if debug:
            print(ps_script)
            print(r.status_code)
            print(r.std_out)
            print(r.std_err)
        return r.status_code == 0

    def create_ou(self):
        ps_script = 'New-ADOrganizationalUnit -Name "Skoler"'


def main():
    ad_int = AdIntegrator()
    print(ad_int.test_connection())
    print(ad_int.create_user('Vakse Villy', ou='Madafdelingen'))


if __name__ == '__main__':
    main()
