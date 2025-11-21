#!/bin/bash

# Script to update .claudetask/instructions/ from framework-assets

echo "=== Updating .claudetask/instructions from framework ==="
echo ""

FRAMEWORK_PATH="framework-assets/claude-configs/instructions"
TARGET_PATH=".claudetask/instructions"

# Check if framework instructions exist
if [ ! -d "$FRAMEWORK_PATH" ]; then
    echo "❌ Error: Framework instructions not found at $FRAMEWORK_PATH"
    exit 1
fi

# Create target directory if it doesn't exist
mkdir -p "$TARGET_PATH"

# Copy all instruction files
echo "Copying instruction files..."
copied=0
for file in "$FRAMEWORK_PATH"/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$TARGET_PATH/$filename"
        echo "✅ Copied: $filename"
        copied=$((copied + 1))
    fi
done

echo ""
echo "=== Update Complete ==="
echo "Copied $copied instruction files to $TARGET_PATH"
echo ""
echo "Updated files:"
ls -1 "$TARGET_PATH"/*.md | while read file; do
    echo "  - $(basename "$file")"
done
