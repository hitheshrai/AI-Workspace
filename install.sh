#!/usr/bin/env bash
# AI-Workspace Universal Installer
# Sets up the AI-Workspace memory framework on any Linux or macOS device.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$SCRIPT_DIR"
BIN_DIR="$HOME/.local/bin"

echo "=========================================================="
echo "         AI-Workspace Multi-Model Framework Setup         "
echo "=========================================================="

# 1. Verify Python availability
if command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
  echo "✅ Python 3 found (v$PY_VER)"
else
  echo "❌ Error: python3 is required but was not found in PATH." >&2
  exit 1
fi

# 2. Initialize local configuration files if missing
if [[ ! -e "$WORKSPACE_DIR/GLOBAL.md" && ! -L "$WORKSPACE_DIR/GLOBAL.md" ]]; then
  cp "$WORKSPACE_DIR/GLOBAL.md.example" "$WORKSPACE_DIR/GLOBAL.md"
  echo "✅ Initialized GLOBAL.md from template"
else
  echo "ℹ️  GLOBAL.md already exists (preserved)"
fi

if [[ ! -e "$WORKSPACE_DIR/PROJECTS.md" && ! -L "$WORKSPACE_DIR/PROJECTS.md" ]]; then
  cp "$WORKSPACE_DIR/PROJECTS.md.example" "$WORKSPACE_DIR/PROJECTS.md"
  echo "✅ Initialized PROJECTS.md from template"
else
  echo "ℹ️  PROJECTS.md already exists (preserved)"
fi

# 3. Setup home directory universal agent instructions
if [[ ! -e "$HOME/AGENTS.md" && ! -L "$HOME/AGENTS.md" ]]; then
  cp "$WORKSPACE_DIR/templates/AGENTS.md" "$HOME/AGENTS.md"
  echo "✅ Installed universal ~/AGENTS.md"
else
  echo "ℹ️  ~/AGENTS.md already exists (preserved)"
fi

# 4. Install command line utilities to ~/.local/bin
mkdir -p "$BIN_DIR"

chmod +x "$WORKSPACE_DIR/bin/ai-mem" "$WORKSPACE_DIR/bin/init-project-memory"

for command in ai-mem init-project-memory; do
  target="$BIN_DIR/$command"
  source="$WORKSPACE_DIR/bin/$command"
  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    echo "ℹ️  $target already points to this workspace (preserved)"
  elif [[ -e "$target" || -L "$target" ]]; then
    echo "⚠️  Existing $target preserved; add or update the link manually."
  else
    ln -s "$source" "$target"
    echo "✅ Linked $command to $BIN_DIR"
  fi
done

# 5. Check PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo ""
  echo "⚠️  Note: $BIN_DIR is not in your current PATH."
  echo "   Add the following line to your ~/.bashrc or ~/.zshrc:"
  echo '   export PATH="$HOME/.local/bin:$PATH"'
fi

echo ""
echo "=========================================================="
echo "✅ Setup Complete! Run 'ai-mem doctor' to verify setup."
echo "=========================================================="
