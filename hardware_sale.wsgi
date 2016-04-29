import sys
sys.stdout = sys.stderr
sys.path.append('/var/www/hardware_sale/')
from hardware_sale import app as application
