import os
import supabase
from app.db.supa_base import super_supabase

async def save_to_storage(flow_id:str,fileName:str,local_file_path:str):
    
    bucket_path=f"{flow_id}/{fileName}"
    try:
        flow_data_bucket=super_supabase.storage.from_("flow-data").upload(path=bucket_path,file=local_file_path,file_options={"cache-control": "3600", "upsert": "false","content-type":"application/pdf"})
        if flow_data_bucket.full_path:
            os.remove(path=local_file_path)
            # delete with crone
            # dir_path = Path(f"./temp/{flow_id}").resolve()
            # os.removedirs(name=dir_path)
            return True
        return False
    except supabase.SupabaseException as e:
        print(e)
        return False
    