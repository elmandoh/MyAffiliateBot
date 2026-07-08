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
    
    # البارامترات الأساسية التي تتوافق مع توثيق AliExpress الرسمي
    params = {
        "app_key": app_key,
        "format": "json",
        "method": "aliexpress.affiliate.hotproduct.query",
        "sign_method": "hmac",
        "timestamp": timestamp,
        "v": "2.0",
        "fields": "product_title,promotion_link,app_sale_price",
        "commission_rate_min": "1000"
    }

    # ترتيب البارامترات حسب الأبجدية (شرط أساسي لنجاح التوقيع)
    keys = sorted(params.keys())
    sign_str = "".join([f"{k}{params[k]}" for k in keys])
    params["sign"] = hmac.new(app_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest().upper()

    response = requests.get("https://api-sg.aliexpress.com/sync", params=params)
    data = response.json()

    # فحص الأخطاء من علي إكسبريس نفسه
    if "error_response" in data:
        raise Exception(f"AliExpress API Error: {data['error_response']['msg']}")

    # الوصول المباشر للبيانات بدون احتمالات خطأ
    resp = data['aliexpress_affiliate_hotproduct_query_response']['resp_result']['result']
    product = resp['products']['product'][0] # أخذ أول منتج فقط
    
    return {
        "name": product['product_title'],
        "price": product['app_sale_price'],
        "link": product['promotion_link']
    }
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
product = get_aliexpress_product()
prompt = f"Write a casual, helpful US-style recommendation for {product['name']} (Price: {product['price']}). Include link: {product['link']}. Use a friendly tone, ask a question at the end."
post_content = generate_content(prompt)

# النشر + التقرير
bsky.send_post(text=post_content)
post_to_github_report(post_content)
print("تم النشر والتقرير بنجاح!")
