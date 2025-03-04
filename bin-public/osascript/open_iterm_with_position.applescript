on run argv
    -- Get arguments
    set positionToOpenStr to item 1 of argv

    -- Parse position string into a list
    set positionToOpen to my parsePositionString(positionToOpenStr)

    log "Opening iTerm2 with a new window"
    tell application "iTerm2"
        create window with default profile
        activate
    end tell

    log "iTerm2 window created and activated"
    delay 0.3

    -- Wait for iTerm2 window to appear
    tell application "System Events"
        log "Waiting for iTerm2 window to appear"
        repeat until (exists window 1 of application process "iTerm2")
            delay 0.1
        end repeat
        log "iTerm2 window appeared"
    end tell

    -- Set window position
    tell application "System Events"
        tell application process "iTerm2"
            log "Setting position to: {" & item 1 of positionToOpen & ", " & item 2 of positionToOpen & "}"
            set position of window 1 to {item 1 of positionToOpen, item 2 of positionToOpen}

            log "Setting size to: {" & item 3 of positionToOpen & ", " & item 4 of positionToOpen & "}"
            set size of window 1 to {item 3 of positionToOpen, item 4 of positionToOpen}
        end tell
    end tell

    delay 0.3
    log "iTerm2 window opened and positioned successfully"

    return "Successfully opened and positioned iTerm2 window"
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
