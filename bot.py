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
    # توقيع الطلب (Signature) لجلب منتجات عالية العمولة
    app_key = os.environ["ALIEXPRESS_APP_KEY"]
    app_secret = os.environ["ALIEXPRESS_APP_SECRET"]
    timestamp = str(int(time.time() * 1000))
    params = {
        "method": "aliexpress.affiliate.hotproduct.query",
        "app_key": app_key, "format": "json", "timestamp": timestamp,
        "v": "2.0", "sign_method": "hmac",
        "commission_rate_min": "1000", "price_min": "15", "price_max": "100",
        "sort": "commission_rate_desc", "fields": "product_title,promotion_link,app_sale_price"
    }
    params_sorted = "".join([f"{k}{v}" for k, v in sorted(params.items())])
    params["sign"] = hmac.new(app_secret.encode('utf-8'), params_sorted.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    
    response = requests.get("https://api-sg.aliexpress.com/sync", params=params).json()
    product = random.choice(response['aliexpress_affiliate_hotproduct_query_response']['resp_result']['result']['products']['product'])
    return {"name": product['product_title'], "price": product['app_sale_price'], "link": product['promotion_link']}

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
