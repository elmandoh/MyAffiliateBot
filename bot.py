import os
import random
import datetime

from atproto import Client
from groq import Groq
from aliexpress_api import AliexpressApi

# إعدادات العملاء
bsky = Client()
bsky.login(os.environ["BLUESKY_HANDLE"], os.environ["BLUESKY_PASSWORD"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])
ali = AliexpressApi(os.environ["ALIEXPRESS_APP_KEY"], os.environ["ALIEXPRESS_APP_SECRET"], models="api.aliexpress.com")



def get_posting_mode():
    hour = datetime.datetime.now().hour
    # إذا كان الوقت في الذروة، اجعله ينشر أفلييت بشكل مكثف (70% احتمال)
    if 18 <= hour <= 23:
        return "aggressive"
    # غير ذلك، منشورات تفاعلية فقط (للحفاظ على السمعة)
    return "gentle"

# واستخدمها في كود النشر:
mode = get_posting_mode()
if mode == "aggressive":
    content = post_affiliate() # نشر أفلييت
else:
    content = post_value()     # نشر قيمة وتفاعل

def get_ai_content(prompt):
    chat_completion = groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content[:290]

def post_affiliate():
    products = ali.get_hot_products(cat_ids=[34], limit=1) # الإلكترونيات
    p = products[0]
    prompt = f"اكتب منشوراً تسويقياً محفزاً بأسلوب احترافي لمنتج: {p.product_title}. السعر: {p.app_sale_price}. الرابط: {p.promotion_link}. اجعله مشوقاً بدون مبالغة."
    return get_ai_content(prompt)

def post_value():
    topics = ["نصيحة تقنية سريعة", "أحدث صيحات الذكاء الاصطناعي", "كيف تختار أفضل الأدوات الذكية"]
    topic = random.choice(topics)
    prompt = f"اكتب تغريدة قصيرة ومفيدة جداً للمتابعين حول موضوع: {topic}. اجعلها تشجع على النقاش."
    return get_ai_content(prompt)

# التشغيل الذكي (50% أفلييت، 50% تفاعل)
if random.choice([True, False]):
    content = post_affiliate()
else:
    content = post_value()

bsky.send_post(text=content)
print(f"تم النشر بنجاح: {content}")
