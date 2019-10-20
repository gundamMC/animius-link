import sys

import amlink

if __name__ == "__main__":

    if len(sys.argv) <= 1:
        network = amlink.network_controller.NetworkController()

        while True:
            pass

    elif sys.argv[1] == 'createuser':
        username = input('username: ')
        password = input('password: ')

        print('The following user will be created:')
        print('Username:', username)
        print('Password:', password)
        confirm = input('Do you want to continue? (y/n): ')
        if confirm == 'y':
            amlink.users.create_user(username, password)
            print('user created')
        else:
            print('user creation aborted')
            sys.exit()
