from subprocess import run


def change_branch():
    """swich to master branch"""
    run(['git', 'checkout', 'master'])
    run(['git', 'pull'])
    pass


def update_version():
    pass


def package():
    run(['python3', 'setup.py', 'sdist'])
    pass


def upload():
    pass


def add_tag():
    """add release tag on github"""
    pass


def main():
    change_branch()
    update_version()
    package()
    upload()
    add_tag()


if __name__ == '__main__':
    main()
