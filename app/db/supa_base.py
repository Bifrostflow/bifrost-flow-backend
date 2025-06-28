import os
from supabase import create_client,Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
super_key: str = os.environ.get("SUPER_SUPABASE_KEY")
supabase: Client = create_client(url, key)
super_supabase: Client = create_client(url, super_key)