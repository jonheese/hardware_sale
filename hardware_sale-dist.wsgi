import sys
sys.stdout = sys.stderr
sys.path.append('/path/to/webapp/')
from hardware_sale import app as application
