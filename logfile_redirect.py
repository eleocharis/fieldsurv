from kivy.config import Config
from os.path import join, exists, expanduser
from os import makedirs

""" Sets the path to the log file. """
log_path = join(expanduser("~"), 'prgwerk/buidozer/logs')
if not exists(log_path):
    makedirs(log_path)
Config.set('kivy', 'log_dir', log_path)