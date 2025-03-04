on run argv
    -- Get the application name and position from arguments
    set appName to item 1 of argv
    set positionToOpenStr to item 2 of argv

    -- Parse position string into a list
    set positionToOpen to my parsePositionString(positionToOpenStr)

    log "Opening application: " & appName
    log "With position: " & positionToOpenStr

    -- Launch the application
    tell application appName
        activate
    end tell

    -- Wait for application to launch
    delay 1

    -- Set window position
    tell application "System Events"
        tell application process appName
            -- Wait for window to appear
            repeat until exists window 1
                delay 0.5
            end repeat

            -- Set position
            log "Setting position to: {" & item 1 of positionToOpen & ", " & item 2 of positionToOpen & "}"
            set position of window 1 to {item 1 of positionToOpen, item 2 of positionToOpen}

            -- Set size if provided
            if (count of positionToOpen) ³ 4 then
                log "Setting size to: {" & item 3 of positionToOpen & ", " & item 4 of positionToOpen & "}"
                set size of window 1 to {item 3 of positionToOpen, item 4 of positionToOpen}
            end if
        end tell
    end tell

    return "Successfully opened " & appName & " with position " & positionToOpenStr
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
