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

# ---- الكود الأوتوماتيكي بالكامل: سحب وتحويل ديناميكي ----

# ---- الكود الأوتوماتيكي المحدث والمقاوم للأخطاء ----

if __name__ == "__main__":
    # 1. قراءة الـ Tracking ID من الـ Secrets
    TRACKING_ID = os.getenv("ALIEXPRESS_TRACKING_ID", "").strip()
    
    print("🚀 بدء تشغيل البوت الأوتوماتيكي...")
    print("📥 جاري سحب المنتجات الأكثر مبيعاً (Hot Products) حالياً...")
    
    hot_method = "aliexpress.affiliate.hotproducts.get"
    hot_params = {
        "fields": "product_title,product_detail_url,sale_price",
        "target_currency": "USD",  # 🌟 معامل إجباري: العملة بالدولار
        "target_language": "EN",   # 🌟 معامل إجباري: اللغة الإنجليزية
        "page_no": "1",
        "page_size": "1"
    }
    
    try:
        # استدعاء الـ API
        hot_response = call_aliexpress_api(hot_method, hot_params)
        
        # [ذكاء برميجي]: فحص لو السيرفر رفض الطلب من برا خالص قبل ما يدخل في الـ Response
        if "error_response" in hot_response:
            err_data = hot_response["error_response"]
            print(f"❌ رفض من منصة علي إكسبريس: {err_data.get('msg')} | التفاصيل: {err_data.get('sub_msg')}")
        else:
            resp_result = hot_response.get("aliexpress_affiliate_hotproducts_get_response", {}).get("resp_result", {})
            
            if resp_result.get("resp_code") == 200:
                products_list = resp_result.get("result", {}).get("products", {}).get("product", [])
                
                if products_list:
                    # سحب بيانات المنتج الأول أوتوماتيكياً
                    live_product = products_list[0]
                    product_title = live_product.get("product_title")
                    product_url = live_product.get("product_detail_url")
                    price = live_product.get("sale_price")
                    
                    print(f"📦 تم سحب المنتج بنجاح: {product_title}")
                    print(f"💰 السعر الحالي: {price}")
                    print(f"🔗 الرابط الأصلي المسحوب: {product_url}")
                    
                    # 2. خطوة التحويل الفوري لروابط الآفلييت الخاصة بك
                    print("🔄 جاري تحويل الرابط أوتوماتيكياً إلى رابط العمولة الخاص بك...")
                    link_gen_method = "aliexpress.affiliate.link.generate"
                    link_gen_params = {
                        "tracking_id": TRACKING_ID,
                        "promotion_link_type": "0", 
                        "source_values": product_url
                    }
                    
                    link_response = call_aliexpress_api(link_gen_method, link_gen_params)
                    links_result = link_response.get("aliexpress_affiliate_link_generate_response", {}).get("resp_result", {})
                    
                    if links_result.get("resp_code") == 200:
                        affiliate_links = links_result.get("result", {}).get("live_link_list", {}).get("live_link", [])
                        if affiliate_links:
                            my_affiliate_link = affiliate_links[0].get("promotion_link")
                            
                            print("\n==================================================")
                            print("🎉 نجاح باهر! السيستم سحب وحوّل بالكامل أوتوماتيك:")
                            print(f"📢 المنتج: {product_title}")
                            print(f"💸 رابط الآفلييت المبروك: {my_affiliate_link}")
                            print("==================================================\n")
                        else:
                            print("⚠️ السيرفر استجاب ولكن قائمة روابط الآفلييت فارغة.")
                    else:
                        print(f"❌ فشل توليد رابط الآفلييت. السبب: {links_result.get('resp_msg')}")
                else:
                    print("⚠️ قائمة المنتجات الأكثر مبيعاً رجعت فارغة من السيرفر.")
            else:
                print(f"❌ فشل سحب المنتجات. السبب: {resp_result.get('resp_msg')}")
                
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع في الدورة الأوتوماتيكية: {str(e)}")
