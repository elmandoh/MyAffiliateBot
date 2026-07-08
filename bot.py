import os
import requests
from atproto import Client
from groq import Groq

# 1. إعداد العملاء (Clients)
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])

groq = Groq(api_key=os.environ["GROQ_API_KEY"])

def get_aliexpress_product():
    # هنا ستضع الكود الخاص بـ AliExpress API لجلب منتج
    # للتجربة سنستخدم نصاً وهمياً
    return {"name": "ساعة ذكية مميزة", "price": "$25", "link": "https://aliexpress.com/item/123"}

def generate_post(product):
    prompt = f"اكتب منشوراً تسويقياً جذاباً لمنصة Bluesky لهذا المنتج: {product['name']} بسعر {product['price']}. الرابط: {product['link']}"
    
    chat_completion = groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# تنفيذ العمليات
product = get_aliexpress_product()
post_content = generate_post(product)

# النشر
bsky.send_post(text=post_content)
print("تم النشر بنجاح!")
