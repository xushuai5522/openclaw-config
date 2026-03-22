#!/usr/bin/env python3
import json, sys
from pathlib import Path
p = Path.home()/'.openclaw'/'openclaw.json'
obj = json.loads(p.read_text())
provider = obj.get('models', {}).get('providers', {}).get('Claude-url', {})
key = provider.get('apiKey', '').strip()
if not key:
    sys.exit('Claude-url apiKey not found in ~/.openclaw/openclaw.json')
print(key)
