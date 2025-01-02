#!/usr/bin/env zsh

function dotfiles-unpack() {
  # Set base directory
  base_dir="$HOME/.oh-my-zsh/custom"

  # Create temp directory for extraction
  timestamp=$(date +%Y%m%d_%H%M%S)
  temp_dir="/tmp/custom_unpack_$timestamp"
  mkdir -p "$temp_dir"

  # Look for custom.zip in Downloads folder
  zip_file="$HOME/Downloads/custom.zip"

  if [ ! -f "$zip_file" ]; then
    echo "Error: custom.zip not found in Downloads folder"
    exit 1
  fi

  # Extract zip to temp directory
  if unzip -q "$zip_file" -d "$temp_dir"; then
    # Copy contents to oh-my-zsh custom directory
    if cp -r "$temp_dir"/* "$base_dir/"; then
      echo "Successfully unpacked custom.zip to oh-my-zsh custom directory"
      # Clean up temp directory
      rm -rf "$temp_dir"
    else
      echo "Error: Failed to copy files to oh-my-zsh custom directory"
      rm -rf "$temp_dir"
      exit 1
    fi
  else
    echo "Error: Failed to extract zip file"
    rm -rf "$temp_dir"
    exit 1
  fi
}
