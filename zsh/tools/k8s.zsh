# Kubernetes aliases and functions

# k9s with specific contexts and auto-authentication
function k9sprd() {
  local profile="Perfil_l5-732207930936"
  local context="arn:aws:eks:sa-east-1:732207930936:cluster/cluster-eks-prd"
  
  # Check if profile is authenticated
  if ! aws sts get-caller-identity --profile "$profile" >/dev/null 2>&1; then
    echo "Not authenticated for $profile. Logging in..."
    aws sso login --profile "$profile"
  fi
  
  EDITOR=vim k9s --context "$context"
}

function k9shml() {
  local profile="Perfil_l5-665053502207"
  local context="arn:aws:eks:us-west-2:665053502207:cluster/cluster-eks-hml-default"
  
  # Check if profile is authenticated
  if ! aws sts get-caller-identity --profile "$profile" >/dev/null 2>&1; then
    echo "Not authenticated for $profile. Logging in..."
    aws sso login --profile "$profile"
  fi
  
  EDITOR=vim k9s --context "$context"
}