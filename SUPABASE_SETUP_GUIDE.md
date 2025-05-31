# Supabase Setup Guide for Morvo AI

## 🎯 Quick Setup Steps

### 1. Get Your Service Role Key
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select project: `teniefzxdikestahndur`
3. Settings → API → Copy "service_role" key
4. Update `.env` file: `SUPABASE_SERVICE_ROLE_KEY="your_key_here"`

### 2. Apply Database Migration

**Option A: Automated (Recommended)**
```bash
python database/apply_migration.py
```

**Option B: Manual**
1. Copy contents of `database/morvo_agents_migration.sql`
2. Supabase Dashboard → SQL Editor → Paste & Run

### 3. Verify Tables Created

Check in Supabase Dashboard → Table Editor for these 11 new tables:
- ✅ `agent_results` - M1-M5 agent outputs
- ✅ `semrush_data` - SEMrush API cache
- ✅ `semrush_keywords` - Keyword tracking
- ✅ `semrush_competitors` - Competitor analysis
- ✅ `marketing_campaigns` - Campaign management
- ✅ `campaign_metrics` - Performance tracking
- ✅ `social_accounts` - Social media setup
- ✅ `social_mentions` - Brand monitoring
- ✅ `content_calendar` - Content strategy
- ✅ `content_performance` - Content metrics
- ✅ `bi_reports` - Business intelligence

## 🔐 Security Features

- **Row Level Security (RLS)** enabled on all tables
- **User isolation** - users only see their own data
- **Foreign keys** to existing `auth.users` table
- **Data validation** with CHECK constraints

## 🚀 Integration Ready

Your database now supports:
- ✅ M1-M5 agent result storage
- ✅ SEMrush data caching (6-24 hour TTL)
- ✅ Social media monitoring
- ✅ Campaign performance tracking
- ✅ Content calendar management
- ✅ Business intelligence reports
- ✅ Arabic language support (default: 'ar')

## 📊 Sample Queries

### Get Agent Results
```sql
SELECT * FROM agent_results 
WHERE user_id = auth.uid() 
AND agent_id = 'm1' 
ORDER BY created_at DESC;
```

### Get Campaign Performance
```sql
SELECT c.name, cm.* 
FROM marketing_campaigns c
JOIN campaign_metrics cm ON c.id = cm.campaign_id
WHERE c.user_id = auth.uid()
ORDER BY cm.metric_date DESC;
```

### Get SEMrush Keywords
```sql
SELECT keyword, difficulty_score, search_volume, cpc
FROM semrush_keywords 
WHERE user_id = auth.uid()
AND domain = 'yourwebsite.com'
ORDER BY search_volume DESC;
```

## 🔄 Next Steps

1. ✅ **Complete database setup**
2. 🚀 **Deploy FastAPI backend to Railway**
3. 🔗 **Connect React frontend to Railway API**
4. 📊 **Test M1-M5 agent workflows**
5. 🎯 **Start using Morvo AI platform!**

---

**Need Help?** All tables are documented in the migration SQL file with detailed comments.
