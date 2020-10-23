import os.path
import os

# Install packages if needed, then import them
try:
    import pyodbc
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'pyodbc'])
    import pyodbc

try:
    import pandas as pd
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'pandas'])
    import pandas as pd




