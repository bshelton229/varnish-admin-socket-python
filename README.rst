.. include globals.rst

Varnish Admin Socket
=====================

A simple python library to administer Varnish over the administration socket. The library can use shared secret authentication. I have only tested it against Varnish 2.1.5.

This was heavily inspired by Tim Whitlock's wonderful PHP library (http://github.com/timwhitlock/php-varnish).

Usage::

  from varnish_admin_socket import VarnishAdminSocket
  varnish = VarnishAdminSocket()
  
  # Optionally set host, port, and secret
  # host defaults to 127.0.0.1, port defaults to 6082, secret defaults to False
  varnish.host = '127.0.0.1'
  varnish.port = 6082
  # You probably want to add a newline, this is usually read from a file.
  varnish.secret = "123\n"

  # Connect to Varnish
  varnish.connect()
  
  # Purge Commands
  varnish.purge_url('^/cached')
  varnish.purge('req.http.host ~ example.com && req.url ~ ^/cached$')

  # Run Stats
  print varnish.stats()
  
  # Quit and close the connection
  varnish.quit()
