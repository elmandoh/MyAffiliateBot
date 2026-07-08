import os
import random
import requests
import hmac
import hashlib
import time
from atproto import Client
from groq import Groq


# بعد تثبيت المكتبة أو وضعها في المجلد
from aliextop.api.rest import AliexpressAffiliateHotproductQueryRequest
from aliextop.api import TopApiClient

# 1. إعداد العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

def get_aliexpress_product():
    # إعداد العميل الرسمي
    client = TopApiClient(app_key=os.environ["ALIEXPRESS_APP_KEY"], 
                          app_secret=os.environ["ALIEXPRESS_APP_SECRET"], 
                          top_gateway_url="https://api-sg.aliexpress.com/sync")
    
    # طلب المنتج باستخدام الكلاس الجاهز (بدون تعقيد التوقيع)
    req = AliexpressAffiliateHotproductQueryRequest()
    req.commission_rate_min = "1000"
    req.fields = "product_title,promotion_link,app_sale_price"
    
    try:
        resp = client.execute(req)
        # المكتبة ستقوم بإرجاع البيانات جاهزة ومنظمة
        # هنا تتعامل مع الرد مباشرة
        return resp.get('products')[0] 
    except Exception as e:
        print(f"Error using SDK: {e}")
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
