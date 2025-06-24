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
