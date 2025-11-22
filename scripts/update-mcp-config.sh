#!/bin/bash
# Update MCP configuration to remove hardcoded project IDs

DB_PATH="/Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework/claudetask/backend/data/claudetask.db"

echo "🔧 Updating MCP configuration to use auto-detection..."

# Remove hardcoded PROJECT_ID from default config
sqlite3 "$DB_PATH" "UPDATE default_mcp_configs SET config = json_remove(config, '$.env.CLAUDETASK_PROJECT_ID') WHERE name = 'claudetask';"

echo "✅ Default MCP config updated"

# Show updated config
echo ""
echo "📋 Updated configuration:"
sqlite3 "$DB_PATH" "SELECT config FROM default_mcp_configs WHERE name = 'claudetask';" | jq .

echo ""
echo "⚠️  IMPORTANT: Restart Claude Code to apply changes!"
echo ""
echo "After restart, the MCP server will automatically detect project IDs by path."
