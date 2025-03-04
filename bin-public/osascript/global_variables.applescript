-- Global window position variables for 3 screens
global firstScreenFull
global secondScreenFull
global thirdScreenFull

global firstScreenFirstHalf
global firstScreenSecondHalf
global secondScreenFirstHalf
global secondScreenSecondHalf
global thirdScreenFirstHalf
global thirdScreenSecondHalf

global firstScreenBigLeft
global firstScreenSmallLeft

-- Screen 1 Full Screen: x = 0, y = 38, width = 1728, height = 1079
set firstScreenFull to {0, 38, 1728, 1079}

-- Screen 2 Full Screen: x = 1728, y = 37, width = 1920, height = 1080
set secondScreenFull to {1728, 37, 1920, 1080}

-- Screen 3 Full Screen: x = 3648, y = 37, width = 1920, height = 1080
set thirdScreenFull to {3648, 37, 1920, 1080}

-- For Screen 1, split the full area into two halves:
set firstScreenFirstHalf to {0, 38, 864, 1079}
set firstScreenSecondHalf to {864, 38, 864, 1079}

-- For Screen 2, splitting the full area in half:
set secondScreenFirstHalf to {1728, 37, 960, 1080}
set secondScreenSecondHalf to {2688, 37, 960, 1080}

-- For Screen 3, splitting the full area in half:
set thirdScreenFirstHalf to {3648, 37, 960, 1080}
set thirdScreenSecondHalf to {4608, 37, 960, 1080}

-- For Screen 1 big and small left sections (using an 80/20 split):
set firstScreenBigLeft to {0, 38, 1382, 1079}  -- roughly 80% of 1728 is 1382
set firstScreenSmallLeft to {1382, 38, 346, 1079} -- remainder: 1728 - 1382 = 346

-- Define desktop codes
global desktop1
global desktop2
global desktop3
global desktop4
global desktop5
global desktop6
global desktop7
global desktop8
global desktop9
global desktop10

set desktop1 to 18
set desktop2 to 19
set desktop3 to 20
set desktop4 to 21
set desktop5 to 23
set desktop6 to 22
set desktop7 to 26
set desktop8 to 28
set desktop9 to 25
set desktop10 to 29

-- Return 1 to indicate success
return 1
