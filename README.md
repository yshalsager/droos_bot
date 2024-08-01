# بوت الدروس العلمية

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=flat&labelColor=00457C&logo=PayPal&logoColor=white&link=https://www.paypal.me/yshalsager)](https://www.paypal.me/yshalsager)
[![Patreon](https://img.shields.io/badge/Patreon-Support-F96854?style=flat&labelColor=F96854&logo=Patreon&logoColor=white&link=https://www.patreon.com/XiaomiFirmwareUpdater)](https://www.patreon.com/XiaomiFirmwareUpdater)
[![Liberapay](https://img.shields.io/badge/Liberapay-Support-F6C915?style=flat&labelColor=F6C915&logo=Liberapay&logoColor=white&link=https://liberapay.com/yshalsager)](https://liberapay.com/yshalsager)

بوت تليجرام مكتوب بلغة بايثون لعرض المواد العلمية لبعض الشيوخ بطريقة منظمة وسهلة التعديل للمشرفين على البوت.

## ميزات البوت

- عرض سلاسل الدروس العلمية مهما كان عددها بطريقة منظمة ومقسمة إلى صفحات تشبه نتائج محركات البحث.
- عرض محتوى كل سلسلة بنفس الطريقة، مع أزرار لإرسال النسخ الصوتية والمرئية وتفريغات وتلخيصات الدروس.
- البحث في محتوى البوت.
- التواصل مع المشرفين.
- إرسال مواد لمشرفي البوت.
- الوصول السريع لوظائف البوت عن طريق لوحة مفاتيح أزرار.
- الرد على المستخدمين بالرد على رسائلهم داخل مجموعة استلام الرسائل.
- إحصائيات مستخدمي البوت وأكثر السلاسل والدروس طلبا (للمشرفين فقط). [`/stats`]
- إرسال رسالة لكل المشتركين في البوت (للمشرفين فقط). [`/broadcast` في رد على رسالة]
- إمكانية إعادة تشغيل البوت لتحميل البيانات مرة أخرى من التليجرام مباشرة (للمشرفين فقط). [`/restart`]
- تحديث الكود الخاص بالبوت في حالة استخدام git. [`/update`]

## كيفية استخدام البوت

- ابدأ البوت عن طريق الضغط على زر start أو البَدْء، ثم استخدم لوحة اﻷزرار لاستخدام وظائف البوت المختلفة مثل "السلاسل
  العلمية - البحث عن سلسلة - إرسال مواد - التواصل والاقتراحات".

## كيفية عمل البوت

البوت يعتمد
على [Google Sheet](https://docs.google.com/spreadsheets/d/1o2016c9JQDROnhAhveKq70pF07_FozozP2xF7ekijTM/edit?usp=sharing)
يقوم المشرفين والمتطوعين بملئها بالشكل التالي:

| series           | lecture      | book                                             | main                                             | video                                            | voice                                            | text                                             | summary |
|------------------|--------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|---------|
| اسم السلسلة      | رقم المحاضرة | كتاب                                             | أهم المحاور                                      | مرئي                                             | صوتي                                             | تفريغ                                            | تلخيص   |
| سلسلة دروس تفسير | 1            | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) |         |

- series: اسم السلسلة: اسم سلسلة الدروس
- lecture: رقم المحاضرة: رقم الدرس داخل سلسلة الدروس
- book: الكتاب: رابط تليجرام لملف PDF الكتاب الذي يشرح في السلسلة أو صوت أو فيديو أو مستند به أهم محاور الدرس
- main: أهم المحاور: رابط تليجرام لصورة أو صوت أو فيديو أو مستند به أهم محاور الدرس
- video: مرئي: رابط تليجرام لنسخة الفيديو من الدرس
- voice: صوتي: رابط تليجرام للنسخة الصوتية من الدرس
- text: تفريغ: رابط تليجرام لمستند تفريغ الدرس
- summary: تلخيص: رابط تليجرام لمستند ملخص الدرس

يحول البوت الرسائل للمستخدمين بالاعتماد على روابط المواد.

## إعداد البوت (للمطورين)

### إعداد حساب خدمة للتعامل مع Google Sheet

- ادخل إلى منصة جوجل للمطورين وأنشئ مشروعا إن لم يكن لديك واحد، ثم فعل الوصول
  إلى [واجهة برمجة Google Sheet](https://console.developers.google.com/marketplace/product/google/sheets.googleapis.com).
- ادخل إلى [صفحة إعداد الصلاحيات](https://console.developers.google.com/apis/api/sheets.googleapis.com/credentials)،
  وأضف حساب خدمة جديد بصلاحيات القراءة فقط "viewer".
- أنشئ مفاتيح للحساب ثم حمل ملف ال JSON إلى مجلد المشروع باسم `service_account.json`.
- أضف عناوين حسابات الخدمة إلى Google Sheet التي بها المواد لتتمكن الحسابات من الوصول إليها.

### إعداد ملف التهيئة

- انسخ هذا المستودع.
- انسخ ملف `config.example.json` باسم `config.json` واملأ المعلومات المطلوبة:

|      البيانات       |                             معلومات                              |                                                                                    ملاحظات                                                                                     |
|:-------------------:|:----------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    tg_bot_token     |            التوكن الخاص بواجهة برمجة تليجرام للبوتات             |                                                                                     إجباري                                                                                     |
|    tg_bot_admins    |                     قائمة معرفات مشرفي البوت                     |                                                                                     إجباري                                                                                     |
| tg_feedback_chat_id | معرف المحادثة التي سيرسل لها الملفات ورسائل التواصل مع المشرفين  |                                                                                     إجباري                                                                                     |
|      sheet_id       |               معرف Google Sheet الخاصة بمواد البوت               |                                                                                     إجباري                                                                                     |
|     sheet_name      |                  اسم Google Sheet التي ستستخدم                   | إجباري<br />يمكن الاستعانة بهذا [النموذج](https://docs.google.com/spreadsheets/d/1o2016c9JQDROnhAhveKq70pF07_FozozP2xF7ekijTM/edit?usp=sharing) لمعرفة كيفية ملء بيانات المواد |
|    data_columns     |          الصفوف التي ستستخدم في عرض المحتوى والبحث فيه           |                                                                      اختياري (يستخدم الافتراضي عند غيابه)                                                                      |
| lecture_components  |                          مكونات كل درس                           |                                                                      اختياري (يستخدم الافتراضي عند غيابه)                                                                      |
|        hide         |               إخفاء بعض الصفوف من القائمة الرئيسية               |                                                                      اختياري (يستخدم الافتراضي عند غيابه)                                                                      |
|       disable       | تعطيل خيارات إرسال مواد - التواصل والاقتراحات - البحث في المحتوى |                                                                      اختياري (يستخدم الافتراضي عند غيابه)                                                                      |

## تشغيل البوت

- استخدم اﻷمر التالي لبدء البوت باستخدام دوكر:

 ```bash
  docker-compose up --build -d
 ```

### تشغيل البوت دون دوكر

#### إعتماديات بايثون

- يحتاج البوت وجود إصدار بايثون 3.9 أو أحدث، وكذلك pip اﻹصدار 19 أو أحدث أو أداة poetry إذا كنت تستخدمها.

##### التثبيت باستخدام poetry

```bash
poetry install
```

##### التثبيت باستخدام Pip

```bash
pip install .
```

#### قاعدة البيانات

يستخدم البوت قاعدة بيانات sqlite. تحقق من أنها مثبتة بنظامك.

#### تشغيل البوت

استخدم اﻷمر التالي لبدء البوت

```bash
python3 -m droos_bot
```

## معلومات تقنية

يستخدم البوت:

- [Python 3](https://python.org/)
- [Docker](https://www.docker.com/)

ومكتبات بايثون:

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot/)
- [python-telegram-bot-pagination](https://github.com/ksinn/python-telegram-bot-pagination)
- [https://github.com/burnash/gspread](https://github.com/burnash/gspread)
- [gspread-pandas](https://github.com/aiguofer/gspread-pandas)
