#!/usr/bin/env python3
"""Start backend without database initialization for debugging"""
import os
os.environ['SKIP_DB_INIT'] = 'true'

import subprocess
subprocess.run(["/opt/homebrew/bin/python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"])