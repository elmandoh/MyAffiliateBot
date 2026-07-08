import requests
import json
import os
import random
import requests
import hmac
import hashlib
import time
from atproto import Client
from groq import Groq


# 1. إعداد العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])



def get_aliexpress_product():
    app_key = os.environ["ALIEXPRESS_APP_KEY"]
    app_secret = os.environ["ALIEXPRESS_APP_SECRET"]
    timestamp = str(int(time.time() * 1000))
    
    params = {
        "app_key": app_key,
        "commission_rate_min": "1000",
        "fields": "product_title,promotion_link,app_sale_price",
        "format": "json",
        "method": "aliexpress.affiliate.hotproduct.query",
        "sign_method": "hmac",
        "timestamp": timestamp,
        "v": "2.0"
    }

    # الترتيب الأبجدي الصارم للمفاتيح
    sorted_keys = sorted(params.keys())
    
    # المعيار الصحيح: دمج [Key + Value] لكل البارامترات مرتبة
    # ثم التوقيع باستخدام الـ secret
    sign_str = ""
    for key in sorted_keys:
        sign_str += f"{key}{params[key]}"
    
    # التوقيع باستخدام HMAC-SHA256
    sign = hmac.new(app_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    params["sign"] = sign

    # تنفيذ الطلب
    response = requests.get("https://api-sg.aliexpress.com/sync", params=params)
    data = response.json()
    
    # فحص الرد
    if 'aliexpress_affiliate_hotproduct_query_response' in data:
        resp = data['aliexpress_affiliate_hotproduct_query_response']
        # التحقق من وجود منتجات
        if 'resp_result' in resp and 'result' in resp['resp_result']:
            products = resp['resp_result']['result'].get('products', {}).get('product', [])
            if products:
                return products[0]
                
    return None
def generate_content(prompt):
    completion = groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile"
    )
    return completion.choices[0].message.content[:280]

    # تأكد من هذا الجزء في دالة post_to_github_report
def post_to_github_report(content):
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues"
    # لاحظ أننا نستخدم os.environ['GITHUB_TOKEN'] الذي مررناه من الـ Workflow
    headers = {"Authorization": f"token {os.environ['GITHUB_TOKEN']}"} 
    requests.post(url, json={"title": "Daily Bot Report", "body": f"Published: {content}"}, headers=headers)

# منطق العمل
# --- التشغيل الأساسي ---
product = get_aliexpress_product()

if product:
    # سيتم تنفيذ هذا الجزء فقط إذا تم جلب منتج سليم
    prompt = f"Write a casual, helpful US-style recommendation for {product['name']} (Price: {product['price']}). Include link: {product['link']}."
    post_content = generate_content(prompt)
    bsky.send_post(text=post_content)
    post_to_github_report(post_content)
    print("تم النشر بنجاح!")
else:
    # البوت سيتوقف هنا بسلام ولن يظهر أي خطأ أحمر
    print("لم يتم العثور على منتج سليم. البوت ينهي عمله بسلام.")
    exit(0)
