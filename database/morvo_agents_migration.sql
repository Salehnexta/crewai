-- Morvo AI Marketing Platform - Additional Tables Migration
-- Add these tables to your existing Supabase database
-- Compatible with existing auth.users and dashboard tables

-- =====================================================
-- M1-M5 AGENTS RESULTS STORAGE
-- =====================================================

-- Main table for all agent results (M1-M5)
CREATE TABLE IF NOT EXISTS agent_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_id VARCHAR(10) NOT NULL CHECK (agent_id IN ('m1', 'm2', 'm3', 'm4', 'm5')),
    task_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    execution_time_ms INTEGER DEFAULT 0,
    cost_units INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SEMRUSH DATA STORAGE
-- =====================================================

-- SEMrush API responses and cached data
CREATE TABLE IF NOT EXISTS semrush_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    database_region VARCHAR(10) DEFAULT 'us',
    query_params JSONB,
    response_data JSONB NOT NULL,
    api_cost INTEGER DEFAULT 1,
    is_cached BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SEMrush keyword tracking
CREATE TABLE IF NOT EXISTS semrush_keywords (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    keyword VARCHAR(500) NOT NULL,
    domain VARCHAR(255),
    difficulty_score INTEGER,
    search_volume INTEGER,
    cpc DECIMAL(10,2),
    competition DECIMAL(3,2),
    trends JSONB,
    position INTEGER,
    url TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SEMrush competitor analysis
CREATE TABLE IF NOT EXISTS semrush_competitors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    competitor_domain VARCHAR(255) NOT NULL,
    common_keywords INTEGER,
    se_keywords INTEGER,
    adwords_keywords INTEGER,
    traffic_similarity DECIMAL(5,2),
    competitive_level VARCHAR(20) DEFAULT 'medium',
    last_analyzed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- MARKETING CAMPAIGNS & PROJECTS
-- =====================================================

-- Marketing campaigns managed by agents
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),
    budget DECIMAL(15,2),
    target_market VARCHAR(100),
    start_date DATE,
    end_date DATE,
    goals JSONB, -- Array of campaign goals
    kpis JSONB,  -- Key performance indicators
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign performance metrics from M3 agent
CREATE TABLE IF NOT EXISTS campaign_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id UUID REFERENCES marketing_campaigns(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    cost DECIMAL(10,2) DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    ctr DECIMAL(5,4), -- Click-through rate
    conversion_rate DECIMAL(5,4),
    roas DECIMAL(8,4), -- Return on ad spend
    quality_score DECIMAL(3,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SOCIAL MEDIA MONITORING (M2 AGENT)
-- =====================================================

-- Social media accounts being monitored
CREATE TABLE IF NOT EXISTS social_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    account_handle VARCHAR(255) NOT NULL,
    account_id VARCHAR(255),
    access_token TEXT, -- Encrypted
    is_active BOOLEAN DEFAULT TRUE,
    last_monitored TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Social media mentions and monitoring results
CREATE TABLE IF NOT EXISTS social_mentions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    social_account_id UUID REFERENCES social_accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    mention_type VARCHAR(50), -- post, comment, mention, hashtag
    content TEXT,
    author_handle VARCHAR(255),
    author_followers INTEGER,
    engagement_count INTEGER DEFAULT 0,
    sentiment_score DECIMAL(3,2), -- -1 to 1
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    is_crisis BOOLEAN DEFAULT FALSE,
    crisis_level VARCHAR(20), -- low, medium, high, critical
    post_url TEXT,
    mentioned_at TIMESTAMP WITH TIME ZONE,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CONTENT STRATEGY (M4 AGENT)
-- =====================================================

-- Content calendar and strategy
CREATE TABLE IF NOT EXISTS content_calendar (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    content_type VARCHAR(50), -- blog, social_post, video, infographic
    platform VARCHAR(50), -- facebook, instagram, linkedin, twitter, website
    content_text TEXT,
    content_assets JSONB, -- URLs to images, videos, etc.
    hashtags TEXT[],
    target_audience VARCHAR(255),
    language VARCHAR(10) DEFAULT 'ar',
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'scheduled', 'published', 'archived')),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content performance metrics
CREATE TABLE IF NOT EXISTS content_performance (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content_id UUID REFERENCES content_calendar(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,4),
    reach INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ANALYTICS & BUSINESS INTELLIGENCE (M5 AGENT)
-- =====================================================

-- Business intelligence reports and dashboards
CREATE TABLE IF NOT EXISTS bi_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    report_name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50), -- roi_analysis, market_trends, competitor_analysis
    data_sources JSONB, -- Array of data sources used
    report_data JSONB NOT NULL,
    insights JSONB, -- Key insights from M5 agent
    recommendations JSONB, -- Action recommendations
    time_period_start DATE,
    time_period_end DATE,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Agent results indexes
CREATE INDEX IF NOT EXISTS idx_agent_results_user_id ON agent_results(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_results_agent_id ON agent_results(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_results_created_at ON agent_results(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_results_status ON agent_results(status);

-- SEMrush data indexes
CREATE INDEX IF NOT EXISTS idx_semrush_data_user_id ON semrush_data(user_id);
CREATE INDEX IF NOT EXISTS idx_semrush_data_domain ON semrush_data(domain);
CREATE INDEX IF NOT EXISTS idx_semrush_data_type ON semrush_data(data_type);
CREATE INDEX IF NOT EXISTS idx_semrush_data_fetched_at ON semrush_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_semrush_keywords_user_id ON semrush_keywords(user_id);
CREATE INDEX IF NOT EXISTS idx_semrush_keywords_domain ON semrush_keywords(domain);

-- Campaign indexes
CREATE INDEX IF NOT EXISTS idx_campaigns_user_id ON marketing_campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON marketing_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaign_metrics_campaign_id ON campaign_metrics(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_metrics_date ON campaign_metrics(metric_date);

-- Social media indexes
CREATE INDEX IF NOT EXISTS idx_social_accounts_user_id ON social_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_social_mentions_user_id ON social_mentions(user_id);
CREATE INDEX IF NOT EXISTS idx_social_mentions_sentiment ON social_mentions(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_social_mentions_crisis ON social_mentions(is_crisis);

-- Content indexes
CREATE INDEX IF NOT EXISTS idx_content_calendar_user_id ON content_calendar(user_id);
CREATE INDEX IF NOT EXISTS idx_content_calendar_platform ON content_calendar(platform);
CREATE INDEX IF NOT EXISTS idx_content_calendar_scheduled_at ON content_calendar(scheduled_at);

-- BI reports indexes
CREATE INDEX IF NOT EXISTS idx_bi_reports_user_id ON bi_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_bi_reports_type ON bi_reports(report_type);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE agent_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE semrush_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE semrush_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE semrush_competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketing_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_mentions ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE bi_reports ENABLE ROW LEVEL SECURITY;

-- Create policies for user data isolation
CREATE POLICY "Users can only access their own agent results" ON agent_results
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own SEMrush data" ON semrush_data
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own keywords" ON semrush_keywords
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own competitors" ON semrush_competitors
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own campaigns" ON marketing_campaigns
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own campaign metrics" ON campaign_metrics
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own social accounts" ON social_accounts
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own social mentions" ON social_mentions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own content" ON content_calendar
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own content performance" ON content_performance
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own BI reports" ON bi_reports
    FOR ALL USING (auth.uid() = user_id);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_agent_results_updated_at BEFORE UPDATE ON agent_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON marketing_campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_calendar_updated_at BEFORE UPDATE ON content_calendar
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
