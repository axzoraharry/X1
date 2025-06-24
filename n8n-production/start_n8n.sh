#!/bin/bash
cd /app/n8n-production
export $(cat .env | xargs)
echo "🎯 Starting n8n Production Instance..."
echo "📡 Web UI will be available at: http://localhost:5678"
echo "🔐 Username: axzora | Password: axzora2024!"
echo ""
npx n8n start --tunnel
