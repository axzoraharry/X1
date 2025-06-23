# n8n Workflow Integration Guide for Axzora Mr. Happy 2.0

## 🚀 Overview

This guide shows how the **n8n workflows repository** (https://github.com/Zie619/n8n-workflows.git) integrates with your **Axzora Mr. Happy 2.0** application to provide powerful automation capabilities.

## 🏗️ Architecture

```
Axzora App → Automation Service → n8n Workflows → External Services
    ↑                                              ↓
    ←───────── Webhook Responses ←──────────────────
```

## 🔧 Integration Components

### 1. Backend Integration (`/app/backend/`)

#### **Automation Routes** (`routes/automation.py`)
- `/api/automation/trigger/{automation_type}` - Trigger workflows
- `/api/automation/webhook/n8n` - Receive n8n callbacks
- `/api/automation/notifications/send` - Send notifications
- `/api/automation/ai/process-transaction` - AI processing
- `/api/automation/backup/user-data` - Data backup

#### **Services**
- **AutomationService** (`services/automation_service.py`) - Core automation logic
- **NotificationService** (`services/notification_service.py`) - Multi-channel notifications
- **WalletService** (enhanced) - Auto-triggers on transactions

#### **Models** (`models/automation.py`)
- `AutomationTrigger` - Trigger events
- `WebhookPayload` - n8n responses
- `NotificationPreferences` - User settings

### 2. Frontend Integration (`/app/frontend/src/`)

#### **Services**
- `automationService.js` - API communication layer

#### **Components**
- `AutomationDashboard.jsx` - Control panel
- `NotificationPreferences.jsx` - User settings

## 📋 Available n8n Workflows

Based on the repository analysis, here are the workflows and their integrations:

### 1. **Messaging Workflows** 🔔

| Workflow | File | Integration |
|----------|------|-------------|
| Telegram Automation | `0001_Telegram_Schedule_Automation_Scheduled.json` | Transaction notifications, booking confirmations |
| Slack Notifications | `0002_Slack_Notification_Automation_Triggered.json` | System alerts, user activity notifications |

**Integration Points:**
- **Transaction Notifications**: Auto-triggered on wallet credit/debit
- **Booking Confirmations**: Travel, recharge, e-commerce orders
- **Low Balance Alerts**: When HP balance < 1.0

### 2. **AI/ML Workflows** 🤖

| Workflow | File | Integration |
|----------|------|-------------|
| OpenAI Processing | `0003_OpenAI_Data_Processing_Manual.json` | Spending insights, recommendations |

**Integration Points:**
- **Transaction Analysis**: AI-powered spending pattern analysis
- **Personalized Recommendations**: Based on user behavior
- **Budget Insights**: Monthly trends and suggestions

### 3. **Database Workflows** 💾

| Workflow | File | Integration |
|----------|------|-------------|
| PostgreSQL Import | `0004_PostgreSQL_Data_Import_Automation_Scheduled.json` | Data synchronization |

**Integration Points:**
- **User Data Sync**: Profile and transaction sync
- **Analytics Data**: Export for reporting
- **Backup Validation**: Ensure data integrity

### 4. **Cloud Storage Workflows** ☁️

| Workflow | File | Integration |
|----------|------|-------------|
| Google Drive Backup | `0005_Google_Drive_File_Backup_Automation_Scheduled.json` | User data backup |

**Integration Points:**
- **Full Data Backup**: Complete user profile and transactions
- **Incremental Backup**: Daily transaction backups
- **Document Storage**: Receipts and confirmations

## 🔗 How Integration Works

### 1. **Automatic Triggers**

Your app automatically triggers workflows when:

```javascript
// Transaction occurs
await WalletService.add_transaction(transaction)
// ↓ Automatically triggers:
// - Transaction notification via Telegram
// - Low balance alert if needed
// - AI analysis for spending insights
```

### 2. **Manual Triggers**

Users can manually trigger workflows:

```javascript
// Send custom notification
await AutomationService.sendNotification(userId, 'telegram', 'Custom message');

// Trigger AI analysis
await AutomationService.analyzeSpendingPatterns(userId, transactionHistory);

// Backup data
await AutomationService.backupUserData(userId, 'full', 'google_drive');
```

### 3. **Webhook Integration**

n8n workflows send results back to your app:

```javascript
// n8n sends webhook to: /api/automation/webhook/n8n
// Your app processes and stores results
```

## 🛠️ Setup Instructions

### 1. **Install n8n**

```bash
# Option 1: Docker (Recommended)
docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n

# Option 2: NPM
npm install n8n -g
n8n start
```

### 2. **Import Workflows**

1. Clone the workflows repository:
   ```bash
   git clone https://github.com/Zie619/n8n-workflows.git
   ```

2. Import workflows into n8n:
   - Open n8n at `http://localhost:5678`
   - Go to Workflows → Import from file
   - Import each `.json` file from the repository

### 3. **Configure Webhooks**

Update your n8n workflows to use these webhook URLs:

| Workflow Type | Webhook URL |
|---------------|-------------|
| Messaging | `http://your-app.com/api/automation/webhook/n8n` |
| AI Processing | `http://your-app.com/api/automation/webhook/n8n` |
| Data Sync | `http://your-app.com/api/automation/webhook/n8n` |
| Backup | `http://your-app.com/api/automation/webhook/n8n` |

### 4. **Environment Configuration**

Update your `.env` file:

```env
# n8n Integration
N8N_BASE_URL="http://localhost:5678"
N8N_API_KEY="your_n8n_api_key"

# External Service Credentials
TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
SLACK_WEBHOOK_URL="your_slack_webhook_url"
OPENAI_API_KEY="your_openai_api_key"
GOOGLE_DRIVE_CREDENTIALS_JSON="path_to_credentials.json"
```

## 🎯 Use Cases & Benefits

### **For Users:**
- **Instant Notifications**: Get real-time updates on all transactions
- **Smart Insights**: AI-powered spending analysis and recommendations
- **Automated Backups**: Never lose your data with automatic cloud backups
- **Multi-Channel Alerts**: Choose how you want to be notified

### **For Business:**
- **Reduced Manual Work**: Automate repetitive tasks
- **Better User Engagement**: Proactive notifications and insights
- **Data Security**: Automated backups and monitoring
- **Scalability**: Handle growing user base with automation

## 📊 Real-World Examples

### 1. **Transaction Flow**
```
User makes payment → 
Wallet debited → 
Telegram notification sent → 
AI analyzes spending → 
Insights delivered
```

### 2. **Low Balance Flow**
```
Balance drops below 1 HP → 
SMS & Telegram alerts sent → 
User gets top-up reminder → 
Backup triggered for safety
```

### 3. **Booking Flow**
```
Travel booking confirmed → 
Email confirmation sent → 
Telegram notification → 
Calendar event created → 
Receipt backed up to Google Drive
```

## 🔧 Testing the Integration

### **Backend Testing**

Test automation endpoints:

```bash
# Test notification
curl -X POST "http://localhost:8001/api/automation/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_id",
    "notification_type": "telegram",
    "message": "Test notification from Axzora!"
  }'

# Test AI processing
curl -X POST "http://localhost:8001/api/automation/ai/process-transaction" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_id",
    "transaction_data": {"amount_hp": 2.5, "description": "Coffee purchase"},
    "analysis_type": "spending_insights"
  }'
```

### **Frontend Testing**

Use the Automation Dashboard to:
1. Send test notifications
2. Trigger AI analysis
3. Initiate data backups
4. View automation history

## 🚀 Next Steps

1. **Set up n8n instance** with the provided workflows
2. **Configure external service credentials** (Telegram, OpenAI, etc.)
3. **Test individual workflows** to ensure they work
4. **Integrate with your app** using the provided APIs
5. **Monitor and optimize** workflow performance

## 🆘 Troubleshooting

### Common Issues:

1. **n8n not responding**: Check if n8n is running on port 5678
2. **Webhooks failing**: Verify webhook URLs in n8n workflows
3. **API key errors**: Check all credentials in `.env` file
4. **Network issues**: Ensure firewall allows communication

### Debug Mode:
Enable debug logging in your app:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

If you need help with the integration:
1. Check n8n documentation: https://docs.n8n.io/
2. Review workflow files in the repository
3. Test individual components step by step
4. Monitor logs for error messages

---

**🎉 You now have a fully integrated n8n automation system with your Axzora Mr. Happy 2.0 app!**

The system will automatically:
- Send notifications for all transactions
- Provide AI-powered insights
- Backup user data regularly
- Handle multi-channel communication
- Scale with your growing user base

**Start small, test thoroughly, and expand automation capabilities as needed!**