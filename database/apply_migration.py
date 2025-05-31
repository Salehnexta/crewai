"""
Supabase Migration Script - Apply Morvo AI Tables
Connects to Supabase and executes the migration SQL
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply the Morvo AI migration to Supabase"""
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ACCESS_TOKEN') or os.getenv('SUPABASE_KEY')  # Try multiple keys
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Missing Supabase credentials!")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase successfully!")
        
        # Read the migration SQL file
        with open('/Users/salehgazwani/crewai/database/morvo_agents_migration.sql', 'r') as file:
            migration_sql = file.read()
        
        print("📄 Migration SQL loaded successfully!")
        print(f"📊 SQL size: {len(migration_sql)} characters")
        
        # Split SQL into individual statements (avoiding issues with multi-statement execution)
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        print(f"🔄 Executing {len(statements)} SQL statements...")
        
        successful_statements = 0
        failed_statements = 0
        
        # Execute each statement individually
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                # Execute SQL statement through Supabase RPC
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                print(f"✅ Statement {i}/{len(statements)} executed successfully")
                successful_statements += 1
                
            except Exception as e:
                # Some statements might fail if they already exist - that's okay
                if "already exists" in str(e).lower():
                    print(f"⚠️  Statement {i}/{len(statements)} skipped (already exists)")
                else:
                    print(f"❌ Statement {i}/{len(statements)} failed: {str(e)}")
                    failed_statements += 1
        
        print(f"\n🎯 Migration Summary:")
        print(f"✅ Successful: {successful_statements}")
        print(f"⚠️  Skipped: {len(statements) - successful_statements - failed_statements}")
        print(f"❌ Failed: {failed_statements}")
        
        if failed_statements == 0:
            print("\n🚀 Migration completed successfully!")
            print("All Morvo AI tables are now ready in your Supabase database!")
        else:
            print(f"\n⚠️  Migration completed with {failed_statements} failures")
            print("Some tables might already exist or there might be permission issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        print("2. Ensure you're using the SERVICE ROLE key (not anon key)")
        print("3. Verify your Supabase project is active")
        return False

def verify_tables():
    """Verify that the tables were created successfully"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ACCESS_TOKEN') or os.getenv('SUPABASE_KEY')  # Try multiple keys
    
    if not supabase_url or not supabase_key:
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # List of tables we expect to have created
        expected_tables = [
            'agent_results',
            'semrush_data', 
            'semrush_keywords',
            'semrush_competitors',
            'marketing_campaigns',
            'campaign_metrics',
            'social_accounts',
            'social_mentions',
            'content_calendar',
            'content_performance',
            'bi_reports'
        ]
        
        print("\n🔍 Verifying table creation...")
        
        for table in expected_tables:
            try:
                # Try to query the table (this will fail if table doesn't exist)
                result = supabase.table(table).select("count", count="exact").limit(0).execute()
                print(f"✅ {table} - Created successfully")
            except Exception as e:
                print(f"❌ {table} - Not found or accessible")
        
        print("\n🎯 Verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Morvo AI Migration Tool")
    print("=" * 50)
    
    # Apply migration
    success = apply_migration()
    
    if success:
        # Verify tables were created
        verify_tables()
        
        print("\n📋 Next Steps:")
        print("1. Check your Supabase Dashboard → Table Editor")
        print("2. Verify all 11 new tables are visible")
        print("3. Test connection from your Railway backend")
        print("4. Deploy your FastAPI backend to Railway")
    else:
        print("\n🔧 Manual Alternative:")
        print("1. Copy the contents of morvo_agents_migration.sql")
        print("2. Go to your Supabase Dashboard → SQL Editor")
        print("3. Paste and run the SQL manually")
