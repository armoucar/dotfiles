on run argv
    -- Get arguments
    set windowName to item 1 of argv
    set positionToOpenStr to item 2 of argv
    set profile to item 3 of argv
    set isFirstLaunch to item 4 of argv

    -- Parse position string into a list
    -- Remove curly braces and split by commas
    set positionToOpen to my parsePositionString(positionToOpenStr)

    log "Starting to open Chrome window with name: " & windowName & ", position: " & positionToOpenStr & ", profile: " & profile
    set chromePath to "/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome"
    set profileOption to "--profile-directory=\"" & profile & "\""
    set newWindowFlag to "--new-window"

    if isFirstLaunch is "true" then
        -- Activate Chrome for the first time
        log "Activating Chrome for the first time"
        tell application "Google Chrome" to activate
    else
        -- Open Chrome detached to avoid hanging
        log "Executing shell script to open Chrome"
        do shell script chromePath & " " & profileOption & " " & newWindowFlag & " >/dev/null 2>&1 &"
    end if

    delay 0.3

    -- Wait for Chrome window to appear
    tell application "System Events"
        log "Waiting for Chrome window to appear"
        repeat until (exists window 1 of application process "Google Chrome")
            delay 0.1
        end repeat
        log "Chrome window appeared"
    end tell

    -- Set window position
    tell application "System Events"
        tell application process "Google Chrome"
            log "Setting position to: {" & item 1 of positionToOpen & ", " & item 2 of positionToOpen & "}"
            set position of window 1 to {item 1 of positionToOpen, item 2 of positionToOpen}

            log "Setting size to: {" & item 3 of positionToOpen & ", " & item 4 of positionToOpen & "}"
            set size of window 1 to {item 3 of positionToOpen, item 4 of positionToOpen}
        end tell
    end tell

    -- Name the Chrome window
    log "Typing search query in Chrome"
    tell application "System Events"
        keystroke "n" using {control down, shift down}
        delay 0.3
        keystroke windowName
        delay 0.3
        key code 36 -- Enter key
    end tell

    delay 0.3
    log "Finished opening Chrome window with name: " & windowName

    return "Successfully opened Chrome window with name " & windowName
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
