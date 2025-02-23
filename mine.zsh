function art-aws-set() {
  export AWS_PROFILE=arthur-dev
  echo "AWS_PROFILE set to arthur-dev"
}

function art-aws-reset() {
  unset AWS_PROFILE
  echo "AWS_PROFILE unset"
}
alias art-aws-unset="art-aws-reset"

function art-aws-print() {
  echo "AWS_PROFILE: $AWS_PROFILE"
}
