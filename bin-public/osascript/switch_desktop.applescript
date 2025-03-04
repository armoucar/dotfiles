on run argv
    -- Get the desktop number from arguments
    set desktopNumber to item 1 of argv as number

    tell application "System Events"
        log "Switching to desktop number: " & desktopNumber
        key code desktopNumber using control down
    end tell

    delay 0.3

    log "Switched to desktop number: " & desktopNumber

    return "Successfully switched to desktop " & desktopNumber
end run
