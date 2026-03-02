#!/usr/bin/env python3
"""
Script to fill form using Chrome DevTools Protocol via existing browser
"""
import json
import subprocess

# Use Chrome DevTools Protocol via curl
# First, get the CDP endpoint from the browser

# Actually, let's use a simpler approach - AppleScript to click
script = '''
tell application "Google Chrome"
    activate
    delay 1
    tell window 1
        -- Try to find and click the CPU dropdown
        set searchFrame to frame 1
        -- Execute JavaScript to click
    end tell
end tell
'''

# Use osascript to click
print("Using AppleScript to click...")
