#!/usr/bin/osascript
tell application "Google Chrome" to activate
delay 0.5
tell application "System Events"
    -- Click at coordinates approximately where the CPU dropdown is
    -- Based on typical screen layout, this should be in the form area
    set mousePos to current application's (do shell script "echo $(/usr/bin/python3 -c 'import Quartz; pos = Quartz.NSEvent.mouseLocation(); print(int(pos.x), int(1080-pos.y))')")
    
    -- Try tabbing to reach the CPU field
    keystroke tab using command down
    delay 0.2
    keystroke tab
    delay 0.2
    keystroke tab
    delay 0.2
    keystroke tab
    delay 0.2
    keystroke tab
end tell
