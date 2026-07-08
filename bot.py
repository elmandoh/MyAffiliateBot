import datetime
import hashlib
import requests

def generate_aliexpress_sign(params, secret_key):
    """
    توليد التوقيع الرقمي (Signature) بالطريقة الصارمة لعلي إكسبريس
    """
    # 1. ترتيب المفاتيح أبجدياً
    sorted_keys = sorted(params.keys())
    
    # 2. بناء سلسلة التشفير: Secret + Key1Value1Key2Value2 + Secret
    sign_string = secret_key
    for key in sorted_keys:
        sign_string += f"{key}{params[key]}"
    sign_string += secret_key
    
    # 3. التشفير بـ MD5 وتحويل الحروف لكبيرة Uppercase
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def call_aliexpress_api(app_key, secret_key, method, api_params={}):
    # الرابط الرسمي للـ API
    url = "https://api-sg.aliexpress.com/sync/api/asyn"
    
    # الـ Parameters الأساسية للنظام (System Parameters)
    sys_params = {
        "app_key": app_key,
        "method": method,
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), # توقيت UTC
        "format": "json",
        "v": "2.0",
        "sign_method": "md5"
    }
    
    # دمج بارامترز النظام مع بارامترز الطلب الخاص بك
    all_params = {**sys_params, **api_params}
    
    # توليد الـ Sign وإضافته للطلب
    all_params["sign"] = generate_aliexpress_sign(all_params, secret_key)
    
    # إرسال الطلب كـ Form Data (وليس JSON)
    try:
        response = requests.post(url, data=all_params)
        return response.json()
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}

# --- تجربة تشغيل للـ API ---
# اكتب بياناتك هنا للتجربة
APP_KEY = "538772" 
SECRET_KEY = "JBnvT1ynfADkeOUk076fP9eXT0OJJzxK "

# تجربة ميثود بسيطة لجلب العروض كمثال للاختبار
test_method = "aliexpress.affiliate.featuredpromo.get" 
test_params = {
    "fields": "promo_desc,image_url,promo_name",
    "page_no": "1",
    "page_size": "10"
}

result = call_aliexpress_api(APP_KEY, SECRET_KEY, test_method, test_params)
print(result)
