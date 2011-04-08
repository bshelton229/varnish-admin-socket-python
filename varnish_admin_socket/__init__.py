"""
Simple Python Varnish socket interface.
"""
import socket, sys, re, string

# Hashlib is necessary to use Secret keys for authentication
# There is an installable module for python 2.3 and 2.4 (I'm talking to you RHEL5)
try:
  import hashlib
  hashlib_loaded = True
except ImportError:
  hashlib_loaded = False

__version__ = '0.1'

class VarnishAdminSocket(object):
  """Varnish Adminiistration Socket Library"""
  def __init__(self):
    """Initialise the Class, default some variables"""
    self.host = '127.0.0.1'
    self.port = 6082
    self.secret = False
    self.conn = False

  # Connect to the socket and attempt authentication if necessary
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
    (code, response) = self.read()
    
    # If we get code 107, we need to try to authenticate
    if code == 107:
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

      (check_code, check_response) = self.send("auth " + c)
      if check_code != 200:
        print "Bad authentication"
        return False
        self.close()
    else:
      return True
    
  # Alias for the stats command
  def stats(self):
    """Return stats"""
    (code, response) = self.send('stats')
    return response
    
  # Alias for the purge command
  def purge(self, expr):
    """Send a purge command to Varnish"""
    (code, response) = self.send("purge %s" % expr)
    return code
      
  # Alias for the purge.url command
  def purge_url(self,path):
    """Send a purge command to Varnish"""
    (code, response) = self.send("purge.url %s" % path)
    return code
    
  # Send a command to the socket
  def send(self, cmd):
    """Sends a command to the socket"""
    if not self.conn:
      raise VarnishAdminSocketError('Your are not connected')
      return False
    
    self.conn.send(cmd + "\n")
    return self.read()
  
  # Read from the socket
  def read(self):
    """Returns the socket information in a hash of code, response"""
    data = self.conn.recv(4096)
    # Split off the first line, it should contain the return code and length
    (return_string,response) = string.split(data, "\n", 1)
    # Match the return code and length
    matches = re.compile('^(\d{3}) (\d+)').findall(return_string)

    # Check to see we got a valid response
    if len(matches):
      # Pull code from the search and make it an integer
      code = int(matches[0][0])
      return [code, response]
    else:
      raise VarnishAdminSocketError('Invalid socket response')
      self.close()
      return False

  # Returns boolean for self.conn
  def connected(self):
    """Return connection status"""
    if self.conn:
      return True
    else:
      return False

  # A more graceful quit, send the quit command first, then close the socket
  def quit(self):
    """Graceful quit"""
    self.send('quit')
    return self.close()

  # Close the socket
  def close(self):
    """Close the socket connection"""
    if self.conn:
      self.conn.close()
    self.conn = False
    return True
    
# Our Exception class
class VarnishAdminSocketError(Exception):
  """VarnishAdminSocket Exception class"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)
