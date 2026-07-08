import os
import datetime
import hashlib
import requests

def generate_aliexpress_sign(params, secret_key):
    """
    توليد التوقيع مع تحويل كل القيم لنصوص بشكل صارم وتنظيفها
    """
    # 1. ترتيب المفاتيح أبجدياً
    sorted_keys = sorted(params.keys())
    
    # 2. بناء سلسلة التشفير مع ضمان تحويل كل قيمة لـ string
    sign_string = secret_key
    for key in sorted_keys:
        sign_string += f"{key}{str(params[key])}"
    sign_string += secret_key
    
    # 3. التشفير
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

# --- قراءة المتغيرات مع تنظيفها تماماً من أي مسافات مخفية .strip() ---
APP_KEY = os.getenv("ALIEXPRESS_APP_KEY", "").strip()
SECRET_KEY = os.getenv("ALIEXPRESS_APP_SECRET", "").strip()

# الدالة المعدلة للإرسال للرابط العالمي الجديد
def call_aliexpress_api(method, api_params={}):
    url = "https://api-sg.aliexpress.com/sync/api/asyn"
    
    sys_params = {
        "app_key": APP_KEY,
        "method": method,
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "2.0",
        "sign_method": "md5"
    }
    
    all_params = {**sys_params, **api_params}
    all_params["sign"] = generate_aliexpress_sign(all_params, SECRET_KEY)
    
    response = requests.post(url, data=all_params, timeout=10)
    return response.json()
    # ---- في آخر الملف تماماً (الأمر الفعلي للتشغيل) ----

if __name__ == "__main__":
    print("🚀 بدء تشغيل البوت وجلب المنتجات من علي إكسبريس...")
    
    # اسم الميثود اللي حابب تجرّب تسحب منها بيانات
    test_method = "aliexpress.affiliate.featuredpromo.get" 
    test_params = {
        "fields": "promo_desc,image_url,promo_name",
        "page_no": "1",
        "page_size": "5"
    }
    
    # استدعاء الدالة وطباعة النتيجة في اللوج
    try:
        response_data = call_aliexpress_api(test_method, test_params)
        print("📥 البيانات المستلمة من علي إكسبريس:")
        print(response_data)
        
        # هنا المفروض ييجي كود الذكاء الاصطناعي (Groq) وكود النشر (Bluesky)
        # بناءً على البيانات اللي رجعت...
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء التشغيل: {str(e)}")
