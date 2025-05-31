# Deploying Morvo AI Marketing Platform to Railway
## Complete Deployment Guide for M1-M5 Agents with MCP, Supabase, and Zapier Integration

This comprehensive guide provides step-by-step instructions for deploying the Morvo AI Marketing Platform with all M1-M5 specialized agents to Railway.

## 🎯 Platform Overview

The Morvo platform deploys 5 specialized AI marketing agents:
- **M1 (Ahmed)**: Strategic Market Analysis & ROI Optimization
- **M2 (Fatima)**: Real-time Social Media Monitoring & Crisis Management  
- **M3 (Mohammed)**: Campaign Tracking & Auto-Optimization
- **M4 (Nora)**: Content Strategy & Calendar Management
- **M5 (Khalid)**: Comprehensive Data Analytics & Business Intelligence

## 🚀 Prerequisites

### Required Accounts & Services
- [Railway Account](https://railway.app/) - For hosting the platform
- [Supabase Account](https://supabase.com/) - For backend database and authentication
- [GitHub Account](https://github.com/) - For repository management
- [OpenAI API Account](https://platform.openai.com/) - For GPT-4o integration
- [Perplexity AI/Serper Account](https://serper.dev/) - For web search and research

### Required API Keys
- OpenAI API Key (GPT-4o)
- Serper API Key (for Perplexity AI research)
- Supabase Project URL and API Keys
- Social Media APIs (Facebook, Twitter, LinkedIn, YouTube)
- Analytics APIs (Google Analytics, Google Ads)
- Business Intelligence APIs (SEMrush, Ahrefs, SimilarWeb)
- Automation APIs (Zapier, Make, IFTTT)

## 📋 Deployment Steps

### Step 1: Prepare Your Repository

Ensure your repository contains these essential files:
- ✅ `Dockerfile` - Railway deployment configuration
- ✅ `railway.toml` - Railway-specific settings
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Environment variable template
- ✅ `morvo_integration_api.py` - Main FastAPI application
- ✅ `agents/morvo_marketing_agents.py` - M1-M5 agent definitions
- ✅ `tasks/morvo_marketing_tasks.py` - Agent task definitions
- ✅ `crews/morvo_marketing_crew.py` - Crew orchestration logic

### Step 2: Set Up Supabase Backend

1. Create a new Supabase project:
   ```bash
   # Visit https://supabase.com/dashboard
   # Click "New Project"
   # Choose your organization and configure project
   ```

2. Note your Supabase credentials:
   - Project URL: `https://your-project.supabase.co`
   - Anon Public Key: `eyJhbGc...`
   - Service Role Key: `eyJhbGc...` (keep this secure)

3. Create necessary tables for agent results and analytics (optional):
   ```sql
   -- Marketing Results Table
   CREATE TABLE marketing_results (
     id SERIAL PRIMARY KEY,
     agent_name VARCHAR(50) NOT NULL,
     company_name VARCHAR(255),
     result_data JSONB,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Campaign Analytics Table  
   CREATE TABLE campaign_analytics (
     id SERIAL PRIMARY KEY,
     campaign_id VARCHAR(255),
     metrics JSONB,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

### Step 3: Set Up Railway Project

1. **Connect to Railway:**
   ```bash
   # Log in to Railway Dashboard
   # Visit https://railway.app/dashboard
   ```

2. **Create New Project:**
   - Click "New Project" 
   - Select "Deploy from GitHub repo"
   - Choose your Morvo repository
   - Railway will auto-detect the Dockerfile

3. **Configure Build Settings:**
   - Build Command: `docker build .`
   - Start Command: `uvicorn morvo_integration_api:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`

### Step 4: Configure Environment Variables

In Railway project → Variables tab, add all environment variables from `.env.example`:

#### Core Configuration
```bash
MORVO_API_KEY=your-secure-morvo-api-key-here
PORT=8000
PYTHONPATH=/app
PYTHONUNBUFFERED=1
LOG_LEVEL=info
```

#### AI/LLM APIs
```bash
OPENAI_API_KEY=sk-your-openai-api-key
SERPER_API_KEY=your-serper-api-key
```

#### Supabase Backend
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```

#### MCP Configuration
```bash
MCP_SERVER_URL=your-mcp-server-url
MCP_API_KEY=your-mcp-api-key
MCP_CONTEXT_WINDOW=32000
```

#### Social Media APIs
```bash
# Facebook/Instagram
FACEBOOK_ACCESS_TOKEN=your-facebook-token
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-secret

# Twitter
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret

# LinkedIn  
LINKEDIN_ACCESS_TOKEN=your-linkedin-token
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-secret

# YouTube
YOUTUBE_API_KEY=your-youtube-api-key
```

#### Analytics & Business Intelligence
```bash
# Google Analytics & Ads
GOOGLE_ANALYTICS_CREDENTIALS=base64-encoded-json
GOOGLE_ANALYTICS_PROPERTY_ID=your-ga4-property-id
GOOGLE_ADS_DEVELOPER_TOKEN=your-google-ads-token

# SEMrush, Ahrefs, etc.
SEMRUSH_API_KEY=your-semrush-key
AHREFS_API_KEY=your-ahrefs-key
SIMILARWEB_API_KEY=your-similarweb-key
```

#### Automation APIs
```bash
# Zapier
ZAPIER_WEBHOOK_URL=your-zapier-webhook-url
ZAPIER_API_KEY=your-zapier-api-key

# Make (Integromat)
MAKE_WEBHOOK_URL=your-make-webhook-url
MAKE_API_KEY=your-make-api-key
```

### Step 5: Deploy and Test

1. **Deploy Application:**
   ```bash
   # Railway will auto-deploy on push to main branch
   # Or manually trigger deployment in Railway dashboard
   ```

2. **Verify Deployment:**
   ```bash
   # Check health endpoint
   curl https://your-railway-app.railway.app/health

   # Expected response:
   {
     "status": "healthy",
     "platform": "Railway", 
     "backend": "Supabase",
     "context_protocol": "MCP",
     "agents": ["M1", "M2", "M3", "M4", "M5"],
     "timestamp": "2024-01-XX:XX:XX"
   }
   ```

3. **Test API Endpoints:**
   ```bash
   # Test demo endpoint
   curl https://your-railway-app.railway.app/api/v2/demo/test

   # Test individual agents (requires API key)
   curl -X POST https://your-railway-app.railway.app/api/v2/agents/m1/strategic-analysis \
     -H "Authorization: Bearer your-morvo-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "company_info": {
         "name": "متجر الأزياء العصرية",
         "industry": "الموضة والأزياء",
         "target_market": "السعودية ودول الخليج"
       }
     }'
   ```

## 🔧 Configuration Options

### Custom Domain Setup
1. In Railway project → Settings → Domains
2. Add your custom domain
3. Configure DNS records as shown
4. Update CORS origins in environment variables

### Scaling Configuration  
```bash
# Railway auto-scales, but you can configure:
# Minimum instances: 1
# Maximum instances: 10  
# Memory limit: 1GB (increase for heavy workloads)
# CPU limit: 1 vCPU (increase for concurrent processing)
```

### Database Optimization
```bash
# Optional: Add PostgreSQL for persistent storage
# Railway → Add Service → PostgreSQL
# Automatically sets DATABASE_URL environment variable
```

## 🔒 Security Best Practices

### Environment Variable Security
- Never commit API keys to repository
- Use Railway's secure environment variable storage
- Rotate API keys regularly
- Implement API key validation in application

### CORS Configuration
```python
# Update in morvo_integration_api.py for production
ALLOWED_ORIGINS = [
    "https://your-morvo-frontend.railway.app",
    "https://your-custom-domain.com"
]
```

### Rate Limiting
```bash
# Configure in environment variables
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100
```

## 📊 Monitoring & Maintenance

### Health Monitoring
- Railway provides built-in monitoring
- Health check endpoint: `/health`
- Monitor logs in Railway dashboard
- Set up alerts for failures

### Performance Optimization
```bash
# Configure gunicorn for production
# Add to Dockerfile:
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "morvo_integration_api:app", "--bind", "0.0.0.0:$PORT"]
```

### Backup Strategy
- Supabase provides automatic backups
- Export agent results regularly
- Version control for configuration changes

## 🔗 Integration Setup

### Zapier Integration
1. Create Zapier account and app
2. Set webhook URLs in environment variables
3. Configure triggers for agent outputs
4. Test automation workflows

### MCP Integration
1. Configure MCP server endpoint
2. Set context window limits
3. Implement secure API communication
4. Monitor context usage and costs

## 🚨 Troubleshooting

### Common Issues

**Deployment Fails:**
```bash
# Check Railway logs for errors
# Verify all required environment variables are set
# Ensure Dockerfile builds locally first
```

**API Key Errors:**
```bash
# Verify all API keys are valid and have correct permissions
# Check rate limits on external APIs
# Ensure environment variables are properly set
```

**Agent Execution Timeouts:**
```bash
# Increase MAX_EXECUTION_TIME environment variable
# Optimize agent tasks for faster execution  
# Consider implementing async processing
```

**Memory Issues:**
```bash
# Increase Railway memory allocation
# Optimize agent memory usage
# Implement result caching
```

## 🎉 Post-Deployment

### Verification Checklist
- [ ] Health endpoint returns 200 status
- [ ] All 5 agents (M1-M5) are accessible
- [ ] API authentication works
- [ ] Supabase connection established
- [ ] External API integrations functional
- [ ] Error logging and monitoring active

### Next Steps
1. Set up frontend integration
2. Configure Zapier automation workflows
3. Implement comprehensive monitoring
4. Add custom analytics dashboard
5. Scale based on usage patterns

## 🆘 Support

For deployment issues:
1. Check Railway documentation
2. Review application logs
3. Verify environment configuration
4. Test API endpoints individually
5. Monitor external API rate limits

**Your Morvo AI Marketing Platform is now ready for production use with all M1-M5 agents deployed on Railway! 🚀**
