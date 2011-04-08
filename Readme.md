## Varnish Admin Socket

Simple python library to administer Varnish. The library can use shared secret authentication.

#### Usage:

    from varnish_admin_socket import VarnishAdminSocket
    varnish = VarnishAdminSocket()
    
    # Optionally set host, port, and secret
    # host defaults to 127.0.0.1, port defaults to 6082, secret defaults to False
    varnish.host = '127.0.0.1'
    varnish.port = 6082
    varnish.secret = '123'

    # Connect to Varnish
    varnish.connect()
    
    # Purge Commands
    varnish.purge_url('^/cached')
    varnish.purge('req.http.host ~ example.com && req.url ^/cached$')

    # Run Stats
    print varnish.stats()
    
    # Quit and close the connection
    varnish.quit()
