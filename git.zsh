#!/bin/bash

alias ggpt="git push origin --tags"
alias gbrprune='git checkout -q main && git for-each-ref refs/heads/ "--format=%(refname:short)" | while read branch; do mergeBase=$(git merge-base main $branch) && [[ $(git cherry main $(git commit-tree $(git rev-parse "$branch^{tree}") -p $mergeBase -m _)) == "-"* ]] && git branch -D $branch; done'

# Function to automate git tagging
increment_tag() {
  # Get the last git tag
  last_tag=$(git describe --tags $(git rev-list --tags --max-count=1))

  # Extract major, minor, patch versions
  IFS='.' read -r major minor patch <<<"${last_tag#v}"

  # Increment the version based on input argument
  case $1 in
    major)
      major=$((major + 1))
      minor=0
      patch=0
      ;;
    minor)
      minor=$((minor + 1))
      patch=0
      ;;
    patch)
      patch=$((patch + 1))
      ;;
    *)
      echo "Usage: $0 {major|minor|patch}"
      return 1
      ;;
  esac

  # Create the new tag
  new_tag="v$major.$minor.$patch"
  git tag $new_tag

  # Optionally, push the tag to the remote repository
  # git push origin $new_tag

  echo "New tag created: $new_tag"
}
