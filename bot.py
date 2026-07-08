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
    # تأكد أن هذه القيم موجودة في الـ Secrets باسمها الصحيح
    app_key = os.environ["ALIEXPRESS_APP_KEY"]
    app_secret = os.environ["ALIEXPRESS_APP_SECRET"]
    
    timestamp = str(int(time.time() * 1000))
    
    # 1. إعداد المعاملات الأساسية (بدون ترتيب مسبق)
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

    # 2. الترتيب الأبجدي (شرط أساسي)
    sorted_keys = sorted(params.keys())
    
    # 3. بناء نص التوقيع (يجب دمج المفتاح والقيمة مباشرة)
    sign_str = ""
    for k in sorted_keys:
        sign_str += k + str(params[k])
    
    # 4. التوقيع النهائي
    sign = hmac.new(app_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    params["sign"] = sign

    # 5. الطلب
    response = requests.get("https://api-sg.aliexpress.com/sync", params=params)
    
    # 6. معالجة الرد
    if response.status_code == 200:
        data = response.json()
        try:
            # الوصول للبيانات
            products = data['aliexpress_affiliate_hotproduct_query_response']['resp_result']['result']['products']['product']
            p = products[0]
            return {"name": p['product_title'], "price": p['app_sale_price'], "link": p['promotion_link']}
        except Exception as e:
            print("خطأ في البيانات:", data) # هنا سنرى بالضبط ما يرسله علي إكسبريس
            return None
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
# --- تشغيل البوت ---
product = get_aliexpress_product()

if product:  # هذا الشرط مهم جداً (يمنع الخطأ إذا لم نجد منتجاً)
    prompt = f"Write a casual, helpful US-style recommendation for {product['name']} (Price: {product['price']}). Include link: {product['link']}. Use a friendly tone, ask a question at the end."
    post_content = generate_content(prompt)
    bsky.send_post(text=post_content)
    post_to_github_report(post_content)
    print("تم النشر والتقرير بنجاح!")
else:
    print("لم يتم العثور على منتج، البوت سينتظر المرة القادمة.")

# النشر + التقرير
bsky.send_post(text=post_content)
post_to_github_report(post_content)
print("تم النشر والتقرير بنجاح!")
