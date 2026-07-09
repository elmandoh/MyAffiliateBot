import os
import datetime
import hashlib
import requests
import logging

# إعداد الـ Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_aliexpress_sign(params, secret_key):
    # ترتيب المفاتيح وضمان أن جميع القيم نصية لمنع أخطاء التشفير
    sorted_keys = sorted(params.keys())
    sign_string = secret_key
    for key in sorted_keys:
        val = params[key]
        sign_string += f"{key}{val if val is not None else ''}"
    sign_string += secret_key
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

# استخدام Session لتحسين الأداء
session = requests.Session()

def call_aliexpress_api(method, api_params={}):
    url = "https://api-sg.aliexpress.com/sync/api/asyn"
    app_key = os.getenv("ALIEXPRESS_APP_KEY", "").strip()
    secret_key = os.getenv("ALIEXPRESS_APP_SECRET", "").strip()
    
    sys_params = {
        "app_key": app_key,
        "method": method,
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "2.0",
        "sign_method": "md5"
    }
    
    all_params = {**sys_params, **api_params}
    all_params["sign"] = generate_aliexpress_sign(all_params, secret_key)
    
    try:
        response = session.post(url, data=all_params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"خطأ في الاتصال بـ API: {e}")
        return None

if __name__ == "__main__":
    tracking_id = os.getenv("ALIEXPRESS_TRACKING_ID", "").strip()
    
    logging.info("🚀 بدء تشغيل البوت الأوتوماتيكي...")
    
    hot_method = "aliexpress.affiliate.hotproduct.query"
    hot_params = {
        "fields": "product_title,product_detail_url,sale_price",
        "target_currency": "USD",
        "tracking_id": tracking_id,
        "page_no": "1",
        "page_size": "1"
    }
    
    res = call_aliexpress_api(hot_method, hot_params)
    
    if res and "aliexpress_affiliate_hotproduct_query_response" in res:
        data = res["aliexpress_affiliate_hotproduct_query_response"].get("resp_result", {})
        if data.get("resp_code") == 200:
            product = data.get("result", {}).get("products", {}).get("product", [{}])[0]
            product_url = product.get("product_detail_url", "").split('?')[0]
            
            logging.info(f"✅ تم سحب المنتج: {product.get('product_title')}")
            
            # توليد الرابط
            link_params = {
                "tracking_id": tracking_id,
                "promotion_link_type": "0",
                "source_values": product_url
            }
            link_res = call_aliexpress_api("aliexpress.affiliate.link.generate", link_params)
            # ... (يمكنك إكمال معالجة النتيجة هنا بنفس الطريقة)
        else:
            logging.error(f"فشل الطلب: {data.get('resp_msg')}")
