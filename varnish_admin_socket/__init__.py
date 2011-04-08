"""
Simple Python Varnish socket interface.
"""
import socket, sys, re, string

# Hashlib is necessary to use Secret keys for authentication
try:
  import hashlib
  hashlib_loaded = True
except ImportError:
  hashlib_loaded = False

__version__ = '0.1'

class VarnishAdminSocket(object):
  
  def __init__(self):
    """
    Initialise the Class, default some variables
    """
    self.host = '127.0.0.1'
    self.port = 6082
    self.secret = False
    self.conn = False

  def connect(self):
    """Make the socket connection"""
    self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Enforce integer for the port
    try:
      self.port = int(self.port)
    except ValueError:
      # Port couldn't be made an integer
      self.close()
      raise VarnishAdminSocketError('Port could not be made an integer')
      return False
    
    # Make the connection
    self.conn.connect( (self.host, self.port) )
    run = self.read()
    
    # If we get code 107, we need to try to authenticate
    if run['code'] == 107:
      # Check to make sure we've defined a secret key
      if not self.secret:
        self.close()
        return False
      
      challenge = string.split(run['response'], "\n", 1)[0]
      secret = self.secret

      # Try for hashlib
      try:
        c = hashlib.sha256("%s\n%s\n%s\n" % (challenge, secret, challenge)).hexdigest()
      except:
        self.close()
        return False

      check_auth = self.send("auth " + c)
      if check_auth['code'] != 200:
        print "Bad authentication"
        return False
        self.close()
    else:
      return True
    
  def stats(self):
    """Return stats"""
    run = self.send('stats')
    return run['response']
    
  def purge(self, expr):
    """Send a purge command to Varnish"""
    run = self.send("purge %s" % expr)
    return run['code']
      
  def purge_url(self,path):
    """Send a purge command to Varnish"""
    run = self.send("purge.url %s" % path)
    return run['code']
    
  def send(self, cmd):
    """Sends a command to the socket"""
    if not self.conn:
      raise VarnishAdminSocketError('Your are not connected')
      return False
    
    self.conn.send(cmd + "\n")
    return self.read()
  
  def read(self):
    """Returns the socket information in a hash of code, response"""
    data = self.conn.recv(4096)
    (return_string,response) = string.split(data, "\n", 1)
    matches = re.compile('^(\d{3}) (\d+)').findall(return_string)
    code = int(matches[0][0])
    return { 'code': code, 'response': response }

  def quit(self):
    """Graceful quit"""
    self.send('quit')
    return self.close()

  def close(self):
    """Close the socket connection"""
    if self.conn:
      self.conn.close()
    self.conn = False
    return True
    
class VarnishAdminSocketError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)
