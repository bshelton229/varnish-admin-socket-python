import os
from distutils.core import setup
from varnish_admin_socket import __version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
    name='varnish-admin-socket',
    version=__version__,
    description='Simple Python Varnish socket interface',
    long_description=read('README.rst'),
    license="MIT",
    author='Bryan Shelton',
    author_email='bryan@sheltonplace.com',
    url='http://github.com/bshelton229/varnish-admin-socket-python',
    packages=['varnish_admin_socket'],
)
