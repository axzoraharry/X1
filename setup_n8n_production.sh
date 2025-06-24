#!/bin/bash

# n8n Production Setup Script for Axzora Mr. Happy 2.0
# This script sets up a real n8n instance with proper configuration

echo "🚀 Setting up Production n8n for Axzora..."

# Create n8n directory
mkdir -p /app/n8n-production
cd /app/n8n-production

# Create environment configuration
cat > .env << EOF
# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=axzora
N8N_BASIC_AUTH_PASSWORD=axzora2024!
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http

# Database Configuration
DB_TYPE=sqlite
DB_SQLITE_DATABASE=/app/n8n-production/database.sqlite

# Security
N8N_ENCRYPTION_KEY=axzora_n8n_encryption_key_2024

# Webhook Configuration
WEBHOOK_URL=http://localhost:5678/

# Logging
N8N_LOG_LEVEL=info
N8N_LOG_OUTPUT=console,file
N8N_LOG_FILE_LOCATION=/app/n8n-production/logs/

# Features
N8N_DISABLE_UI=false
N8N_METRICS=true

# API Keys for Workflows (Demo values)
TELEGRAM_BOT_TOKEN=demo_telegram_token
OPENAI_API_KEY=demo_openai_key
GOOGLE_DRIVE_CREDENTIALS=demo_google_credentials
SLACK_WEBHOOK=demo_slack_webhook
EOF

# Create logs directory
mkdir -p logs

# Create n8n startup script
cat > start_n8n.sh << 'SCRIPT_EOF'
#!/bin/bash
cd /app/n8n-production
export $(cat .env | xargs)
echo "🎯 Starting n8n Production Instance..."
echo "📡 Web UI will be available at: http://localhost:5678"
echo "🔐 Username: axzora | Password: axzora2024!"
echo ""
npx n8n start --tunnel
SCRIPT_EOF

chmod +x start_n8n.sh

# Create workflow import script
cat > import_workflows.sh << 'SCRIPT_EOF'
#!/bin/bash
echo "📥 Importing n8n workflows from repository..."

# Wait for n8n to be ready
while ! curl -s http://localhost:5678 > /dev/null; do
  echo "⏳ Waiting for n8n to start..."
  sleep 2
done

echo "✅ n8n is ready! Workflows can be imported via the web interface."
echo "🌐 Open http://localhost:5678 and go to Workflows > Import from file"
echo "📁 Workflow files are located in: /app/n8n-workflows/workflows/"
SCRIPT_EOF

chmod +x import_workflows.sh

# Create systemd service file for production deployment
cat > n8n-axzora.service << 'SERVICE_EOF'
[Unit]
Description=n8n workflow automation for Axzora
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app/n8n-production
Environment=NODE_ENV=production
ExecStart=/app/n8n-production/start_n8n.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "✅ n8n production setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start n8n: ./start_n8n.sh"
echo "2. Import workflows: ./import_workflows.sh"
echo "3. Configure real API keys in .env file"
echo "4. Update Axzora backend to use http://localhost:5678"
echo ""
echo "🎯 Files created:"
echo "   - .env (n8n configuration)"
echo "   - start_n8n.sh (startup script)"
echo "   - import_workflows.sh (workflow import helper)"
echo "   - n8n-axzora.service (systemd service)"