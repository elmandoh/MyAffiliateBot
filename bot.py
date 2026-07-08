import os
from atproto import Client

# هذا الكود سيتم سحب المتغيرات منه من الـ Secrets
handle = os.environ.get("BLUESKY_HANDLE")
password = os.environ.get("BLUESKY_PASSWORD")

print("البوت بدأ العمل...")
# هنا سنضيف لاحقاً كود جلب منتجات AliExpress وربطه بـ Groq
