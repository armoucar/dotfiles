on run argv
    -- Get arguments
    set positionToOpenStr to item 1 of argv

    -- Parse position string into a list
    set positionToOpen to my parsePositionString(positionToOpenStr)

    log "Setting path for Google Meet application"
    set meetPath to "/Users/U003877/Applications/Chrome\\ Apps.localized/Google\\ Meet.app/Contents/MacOS/app_mode_loader >/dev/null 2>&1 &"

    log "Executing shell script to open Google Meet"
    do shell script meetPath
    delay 0.5

    -- Wait for Google Meet window to appear
    tell application "System Events"
        log "Waiting for Google Meet window to appear"
        repeat until (exists window 1 of application process "app_mode_loader")
            delay 0.1
        end repeat
        log "Google Meet window appeared"
    end tell

    -- Set window position
    tell application "System Events"
        tell application process "app_mode_loader"
            log "Setting position to: {" & item 1 of positionToOpen & ", " & item 2 of positionToOpen & "}"
            set position of window 1 to {item 1 of positionToOpen, item 2 of positionToOpen}

            log "Setting size to: {" & item 3 of positionToOpen & ", " & item 4 of positionToOpen & "}"
            set size of window 1 to {item 3 of positionToOpen, item 4 of positionToOpen}
        end tell
    end tell

    delay 0.3
    log "Google Meet window opened and positioned successfully"

    return "Successfully opened and positioned Google Meet window"
end run

-- Helper function to parse position string into a list
on parsePositionString(posStr)
    -- Remove curly braces if present
    if character 1 of posStr is "{" and character (length of posStr) of posStr is "}" then
        set posStr to text 2 through ((length of posStr) - 1) of posStr
    end if

    -- Split by commas and convert to numbers
    set AppleScript's text item delimiters to ", "
    set posItems to text items of posStr
    set AppleScript's text item delimiters to ""

    -- Create list of position values
    set posList to {}
    repeat with i from 1 to (count of posItems)
        set posItem to item i of posItems
        try
            set end of posList to posItem as number
        on error
            -- If conversion fails, use default value
            set end of posList to 0
        end try
    end repeat

    return posList
end parsePositionString
