Face Unlocker - PAM
===================

Installation
------------

### Installation of the latest versions

Install required packages for building

    ~# apt-get install git devscripts equivs

Build the package

    ~$ cd ./pam-face/
    ~$ sudo mk-build-deps -i debian/control
    ~$ dpkg-buildpackage -uc -us

Install the package

    ~# dpkg -i ../libpam-face*.deb

Install missing dependencies

    ~# apt-get install -f

Setup
-----

Enable PAM Face for a user

    ~# pamface-conf --add-user <username>

Test if everything works well

    ~$ pamface-conf --check-user <username>

Remove user from PAM module

    ~$ pamface-conf --remove-user <username>

