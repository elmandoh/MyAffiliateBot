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
    
    params = {
        "app_key": app_key,
        "format": "json",
        "method": "aliexpress.affiliate.hotproduct.query",
        "sign_method": "hmac",
        "timestamp": str(int(time.time() * 1000)),
        "v": "2.0",
        "fields": "product_title,promotion_link,app_sale_price",
        "commission_rate_min": "1000"
    }

    # الترتيب الأبجدي الصارم (سر نجاح التوقيع)
    sorted_keys = sorted(params.keys())
    sign_str = "".join([f"{k}{params[k]}" for k in sorted_keys])
    
    # إنشاء التوقيع
    sign = hmac.new(app_secret.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    params["sign"] = sign

    response = requests.get("https://api-sg.aliexpress.com/sync", params=params)
    data = response.json()
    
    # فحص النتيجة
    try:
        resp = data.get('aliexpress_affiliate_hotproduct_query_response', {})
        res_result = resp.get('resp_result', {})
        result = res_result.get('result', {})
        products = result.get('products', {}).get('product', [])
        
        if products:
            p = products[0]
            return {"name": p['product_title'], "price": p['app_sale_price'], "link": p['promotion_link']}
    except:
        pass
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
