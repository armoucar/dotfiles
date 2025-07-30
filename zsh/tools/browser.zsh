CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="--profile-directory=Default"

chrome-chatgpt() {
  $CHROME_PATH --app="https://chat.openai.com/" --profile-directory="Profile 1"
}

chrome-keep() {
  $CHROME_PATH --app="https://keep.google.com/" $PROFILE
}

chrome-bootstrap() {
  $CHROME_PATH --app="https://getbootstrap.com/docs" $PROFILE
}

chrome-apps() {
  chrome-chatgpt
  chrome-keep
  chrome-bootstrap
}
