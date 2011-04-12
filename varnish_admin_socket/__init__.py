"""
Simple Python Varnish socket interface.
"""
import socket, sys, re, string

# Hashlib is necessary to use Secret keys for authentication
# There is an installable hashlib module for python 2.3 and 2.4 (I'm talking to you RHEL5)
try:
  import hashlib
  hashlib_loaded = True
except ImportError:
  hashlib_loaded = False

# varnish-admin-socket-python version
__version__ = '0.1'

## Varnish Admin Socket for executing varnishadm CLI commands
## Tested on varnish 2.1.5
class VarnishAdminSocket(object):
  """Varnish Adminiistration Socket Library"""
  def __init__(self, **kwargs):
    """Initialise the Class, default some variables"""
    
    # Check kwargs for overrides
    self.host = kwargs.pop('host', '127.0.0.1')
    self.port = kwargs.pop('port', 6082)
    self.secret = kwargs.pop('secret', False)

    # If auto_connect = True, attempt to connect on instantiation
    self.auto_connect = kwargs.pop('auto_connect', False)
    if self.auto_connect:
      self.connect()
    else:
      self.conn = False

  # Connect to the socket and attempt authentication if necessary
  def connect(self, timeout=5):
    """Make the socket connection"""
    # Connect to the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(1)
    sock.settimeout(timeout)

    # Enforce integer for the port
    try:
      self.port = int(self.port)
    except ValueError:
      # Port couldn't be made an integer
      self.close()
      raise Exception('VarnishAdminSocket: Port could not be made an integer')
      return False
    
    # Make the connection
    sock.connect( (self.host, self.port) )

    # Store the socket makefile
    self.conn = sock.makefile()

    # Close the socket object now that we have makefile
    sock.close()
    (code, response) = self.read()

    # If we get code 107, we need to try to authenticate
    if code == 107:
      # Check to make sure we've defined a secret key
      if not self.secret:
        raise Exception("VarnishAdminSocket: Authentication is required, please set the secret key.")
        self.close()
        return False
      
      challenge = string.split(response, "\n", 1)[0]
      secret = self.secret

      # Try for hashlib
      try:
        c = hashlib.sha256("%s\n%s%s\n" % (challenge, secret, challenge)).hexdigest()
      except:
        self.close()
        return False

      (check_code, check_response) = self.send("auth " + c)
      if check_code != 200:
        raise Exception("VarnishAdminSocket: Bad Authentication")
        return False
        self.close()
    else:
      return True
    
  # Alias for the stats command
  # Returns the response string
  def stats(self):
    """Return stats"""
    (code, response) = self.send('stats')
    return response
    
  # Runs the status command and returns true or false
  def status(self):
    """Runs the status command and returns true or false"""
    (code, response) = self.send('status')
    s = re.search('Child in state (\w+)', response)
    if s:
      if(s.group(1) == "running"):
        return True
      else:
        return False
    else:
      return False
    
  ## Commands ##
  
  # Alias for the purge command
  # Returns the code
  def purge(self, expr):
    """Send a purge command to Varnish"""
    (code, response) = self.send("purge %s" % expr)
    return code
      
  # Alias for the purge.url command
  # Returns the code
  def purge_url(self,path):
    """Send a purge command to Varnish"""
    (code, response) = self.send("purge.url %s" % path)
    return code

  # Runs the purge.list command
  # Returns the response
  def purge_list(self):
    """Runs the purge.list command"""
    (code, response) = self.send("purge.list")
    return response
  
  # Send the start command
  # Returns true or false
  def start(self):
    """Send the start command"""
    (code, response) = self.send("start")
    if code == 200:
      return True
    else:
      return False
    
  # Send the stop command
  # Returns true or false
  def stop(self):
    """Send the stop command"""
    (code, response) = self.send("stop")
    if code == 200:
      return True
    else:
      return False
    
  # Run any varnish command
  # Returns the response and code
  # ok = the code varnish needs to return for this function to return response,
  # otherweise the function returns False
  def command(self, cmd, ok=200):
    """Runs any command against the varnish socket and returns the response"""
    ok = int(ok)
    (code, response) = self.send(cmd)
    if(code == ok):
      return response
    else:
      # Raise an exception
      return False

  # Send a command to the socket
  def send(self, cmd):
    """Sends a command to the socket"""
    if not self.conn:
      raise Exception('Your are not connected')
      return False
    
    self.conn.write("%s\n" % cmd)
    self.conn.flush()
    
    read = self.read()
    if self.auto_connect and not re.match("auth|quit", cmd):
      self.quit()
    return read
  
  # Read from the socket
  def read(self):
    """Returns the socket information in a hash of code, response"""
    # TODO: Raise exceptions here if we can't read
    (code, blen) = self.conn.readline().split()    
    msg = self.conn.read(int(blen)+1)
    
    return [int(code), msg.rstrip()]

  # Returns boolean for self.conn
  def connected(self):
    """Return connection status"""
    if self.conn:
      return True
    else:
      return False

  # A more graceful quit, send the quit command first, then closes the socket
  def quit(self):
    """Graceful quit"""
    self.send('quit')
    return self.close()

  # Close the socket
  def close(self):
    """Close the socket connection"""
    if self.connected():
      self.conn.close()
    self.conn = False
    return True
