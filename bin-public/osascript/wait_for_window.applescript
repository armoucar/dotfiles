on run argv
    -- Get the application name from arguments
    set appName to item 1 of argv

    tell application "System Events"
        log "Waiting for window of application: " & appName
        repeat until (exists window 1 of application process appName)
            delay 0.1
        end repeat

        log "Window found for application: " & appName
    end tell

    return "Successfully found window for " & appName
end run
