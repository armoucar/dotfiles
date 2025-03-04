on run argv
    -- Get arguments
    set appName to item 1 of argv
    set appPath to item 2 of argv
    set filePath to item 3 of argv
    set positionToOpenStr to item 4 of argv

    -- Parse position string into a list
    set positionToOpen to my parsePositionString(positionToOpenStr)

    log "Opening application: " & appName & " from path: " & appPath & " with file: " & filePath
    do shell script "open -a " & quoted form of appPath & " " & quoted form of filePath
    delay 0.5

    -- Wait for window to appear
    tell application "System Events"
        log "Waiting for window of application: " & appName
        repeat until (exists window 1 of application process appName)
            delay 0.1
        end repeat
        log "Window found for application: " & appName
    end tell

    -- Set window position
    tell application "System Events"
        tell application process appName
            log "Setting position to: {" & item 1 of positionToOpen & ", " & item 2 of positionToOpen & "}"
            set position of window 1 to {item 1 of positionToOpen, item 2 of positionToOpen}

            log "Setting size to: {" & item 3 of positionToOpen & ", " & item 4 of positionToOpen & "}"
            set size of window 1 to {item 3 of positionToOpen, item 4 of positionToOpen}
        end tell
    end tell

    delay 0.3
    log "Finished opening and positioning application: " & appName

    return "Successfully opened and positioned " & appName & " with file " & filePath
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
