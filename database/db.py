from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv() 

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def signup_user(email, password, full_name):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}}
        })
        if response.user:
            return response.user, None
        return None, "Signup failed"
    except Exception as e:
        return None, str(e)

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            return response.user, None
        return None, "Login failed"
    except Exception as e:
        return None, str(e)

def save_report(user_id, image_name, annotated_image_b64, detections):
    try:
        result = supabase.table("reports").insert({
            "user_id": user_id,
            "image_name": image_name,
            "annotated_image": annotated_image_b64,
            "total_defects": len(detections),
            "defects": detections
        }).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Save report error: {e}")
        return None

def get_user_reports(user_id):
    try:
        result = supabase.table("reports")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return result.data
    except Exception as e:
        print(f"Get reports error: {e}")
        return []

def get_report_stats(user_id):
    try:
        reports = get_user_reports(user_id)
        stats = {
            "total_inspections": len(reports),
            "total_defects": sum(r.get("total_defects", 0) for r in reports),
            "defect_counts": {},
            "severity_counts": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "recent_reports": reports[:5]
        }
        for r in reports:
            for d in r.get("defects", []):
                d_type = d.get("defect_type", "unknown")
                stats["defect_counts"][d_type] = stats["defect_counts"].get(d_type, 0) + 1
                sev = d.get("severity", "LOW").upper()
                if sev in stats["severity_counts"]:
                    stats["severity_counts"][sev] += 1
        return stats
    except Exception as e:
        print(f"Stats error: {e}")
        return {}