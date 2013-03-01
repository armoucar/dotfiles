csscount() {
  cnt=0
  depth=0
  while read -n 1 char; do
    case $char in
      "{")
        ((depth++))
        ;;
      "}")
        ((depth--))
        if [ "$depth" -eq "0" ]; then
          ((cnt++))
        fi
        ;;
      ",")
        ((cnt++))
        ;;
    esac
  done

  echo $cnt
}
