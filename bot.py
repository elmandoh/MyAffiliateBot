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

# ---- التعديل النهائي لجزء التشغيل الفعلي في آخر ملف bot.py ----

# ---- التعديل الذكي لتفادي قائمة العروض الفاضية ----

if __name__ == "__main__":
    # 1. قراءة الـ Tracking ID
    TRACKING_ID = os.getenv("ALIEXPRESS_TRACKING_ID", "").strip()
    
    print("🚀 بدء تشغيل البوت وجلب البيانات...")
    
    target_url = None
    promo_name = ""
    
    # محاولة جلب العروض العامة أولاً
    promo_method = "aliexpress.affiliate.featuredpromo.get" 
    promo_params = {
        "fields": "promo_desc,image_url,promo_name",
        "page_no": "1",
        "page_size": "1"
    }
    
    try:
        promo_response = call_aliexpress_api(promo_method, promo_params)
        resp_result = promo_response.get("aliexpress_affiliate_featuredpromo_get_response", {}).get("resp_result", {})
        
        if resp_result.get("resp_code") == 200:
            promo_list = resp_result.get("result", {}).get("promo_list", {}).get("featured_promo", [])
            if promo_list:
                target_url = promo_list[0].get("promo_link")
                promo_name = promo_list[0].get("promo_name")
                print(f"📦 تم العثور على عرض رسمي: {promo_name}")
    except Exception as e:
        print(f"⚠️ خطأ أثناء محاولة جلب العروض العامة: {e}")

    # 2. الخطة البديلة: لو الميثود اللي فوق رجعت فاضية، استخدم رابط منتج حقيقي فوراً للتجربة
    if not target_url:
        print("⚠️ لم يتم العثور على عروض عامة حالياً من علي إكسبريس.")
        print("🔄 كخطة بديلة، سيتم استخدام رابط منتج حقيقي للتأكد من عمل نظام الآفلييت...")
        # رابط منتج حقيقي عشوائي من علي إكسبريس للتجربة
        target_url = "https://www.aliexpress.com/item/1005005814523924.html"
        promo_name = "منتج تجاري عشوائي"
        
    print(f"🔗 الرابط المستهدف للتحويل: {target_url}")

    # 3. خطوة توليد رابط الآفلييت الخاص بك
    print("🔄 جاري تحويل الرابط إلى رابط آفلييت خاص بك...")
    try:
        link_gen_method = "aliexpress.affiliate.link.generate"
        link_gen_params = {
            "tracking_id": TRACKING_ID,
            "promotion_link_type": "0", 
            "source_values": target_url 
        }
        
        link_response = call_aliexpress_api(link_gen_method, link_gen_params)
        links_result = link_response.get("aliexpress_affiliate_link_generate_response", {}).get("resp_result", {})
        
        if links_result.get("resp_code") == 200:
            affiliate_links = links_result.get("result", {}).get("live_link_list", {}).get("live_link", [])
            if affiliate_links:
                my_affiliate_link = affiliate_links[0].get("promotion_link")
                
                print("\n==================================================")
                print("🎉 مبروووك! تم توليد رابط الآفلييت الخاص بك بنجاح:")
                print(f"💰 رابط العمولة: {my_affiliate_link}")
                print("==================================================\n")
            else:
                print("⚠️ السيرفر استجاب ولكن قائمة الروابط فارغة.")
        else:
            print(f"❌ فشل توليد الرابط. السبب: {links_result.get('resp_msg')}")
            
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع أثناء التوليد: {str(e)}")
