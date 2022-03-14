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
- البحث عن السلاسل العلمية.
- التواصل مع المشرفين.
- إرسال مواد لمشرفي البوت.
- الوصول السريع لوظائف البوت عن طريق لوحة مفاتيح أزرار.
- إحصائيات مستخدمي البوت وأكثر السلاسل والدروس طلبا (للمشرفين فقط). [`/stats`]
- إرسال رسالة لكل المشتركين في البوت (للمشرفين فقط). [`/broadcast` في رد على رسالة]
- إمكانية إعادة تشغيل البوت لتحميل البيانات مرة أخرى من التليجرام مباشرة (للمشرفين فقط). [`/restart`]


## كيفية استخدام البوت

- ابدأ البوت عن طريق الضغط على زر start أو البَدْء، ثم استخدم لوحة اﻷزرار لاستخدام وظائف البوت المختلفة مثل "السلاسل
  العلمية - البحث عن سلسلة - إرسال مواد - التواصل والإقراحات".

## كيفية عمل البوت

البوت يعتمد
على [Google Sheet](https://docs.google.com/spreadsheets/d/1o2016c9JQDROnhAhveKq70pF07_FozozP2xF7ekijTM/edit?usp=sharing)
يقوم المشرفين والمتطوعين بملئها بالشكل التالي:

| slug        | id        | series           | lecture      | book                                             | main                                             | video                                            | voice                                            | text                                             | summary |
|-------------|-----------|------------------|--------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|---------|
| كود السلسلة | كود الدرس | اسم السلسلة      | رقم المحاضرة | كتاب                                             | أهم المحاور                                      | مرئي                                             | صوتي                                             | تفريغ                                            | تلخيص   |
| har_nwt     | har_nwt1  | سلسلة دروس تفسير | 1            | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) | [https://t.me/channel/4](https://t.me/channel/4) |         |

- slug: كود السلسلة: معرف فريد لكل سلسلة دروس.
- id: كود الدرس: يولد تِلْقائيًا من كود السلسلة + رَقَم المحاضرة
- series: اسم السلسلة: اسم سلسلة الدروس
- lecture: رقم المحاضرة: رقم الدرس داخل سلسلة الدروس
- book: الكتاب: رابط تليجرام لملف PDF الكتاب الذي يشرح في السلسلة أو صوت أو فيديو أو مستند به أهم محاور الدرس
- main: أهم المحاور: رابط تليجرام لصورة أو صوت أو فيديو أو مستند به أهم محاور الدرس
- video: مرئي: رابط تليجرام لنسخة الفيديو من الدرس
- voice: صوتي: رابط تليجرام للنسخة الصوتية من الدرس
- text: تفريغ: رابط تليجرام لمستند تفريغ الدرس
- summary: تلخيص: رابط تليجرام لمستند ملخص الدرس

ثم يقرأ البوت هذه البيانات ويعرضها مقسمة إلى صفحات، ويرسل المواد مباشرة للمستخدم عن طريق ال id الخاص بكل مِلَفّ دون
الحاجة للرفع.

##### ملاحظة

التحدي الأكبر كان جلب ال id الخاص بالملفات، إذ يبدو أن تليجرام يعين file id مختلف لكل ملف بكل حساب أو بوت.

وحلت المشكلة عن طريق:

- إضافة وظيفة للبوت تقوم عندما يرسل حساب مشرف البوت ملف إليه سيرد البوت بال file id الخاص بهذا الملف.
- عمل أداة لأتمتة حساب شخصي، يقرأ روابط الملفات الموجودة على تليجرام من نفس Google Sheet ثم يرسلها للبوت ويقرأ رد البوت
  ثم يستبدل الرابط بالid داخل Google Sheet.

## إعداد البوت (للمطورين)

### إعداد حساب خدمة للتعامل مع Google Sheet

- ادخل إلى منصة جوجل للمطورين وأنشئ مشروعا إن لم يكن لديك واحد، ثم فعل الوصول
  إلى [واجهة برمجة Google Sheet](https://console.developers.google.com/marketplace/product/google/sheets.googleapis.com)
  .
- ادخل إلى [صفحة إعداد الصلاحيات](https://console.developers.google.com/apis/api/sheets.googleapis.com/credentials)،
  وأضف حسابي خدمة جديدين واحد بصلاحيات القراءة فقط "viewer" والثاني بصلاحيات القراءة والكتابة "editor" (تحتاجه أداة
  تحويل الروابط فقط).
- أنشئ مفاتيح لكلا الحسابين ثم حمل ملفات ال JSON الخاصة بالحسابين إلى مجلد المشروع باسم `service_account.json` لحساب
  العرض، واسم `service_account_rw.json` لحساب التعديل على Google Sheet.
- أضف عناوين حسابات الخدمة إلى Google Sheet التي بها المواد لتتمكن الحسابات من الوصول إليها.

### إعداد ملف التهيئة

- انسخ هذا المستودع.
- انسخ ملف `config.json.example` باسم `config.json` و اكتب المعلومات المطلوبة:

```json
{
  "tg_bot_token": "0000000000:aaaaaaaaaaaaaaaaaaaa",
  "tg_bot_admins": [
    1000001,
    1000002,
    1000003
  ],
  "tg_feedback_chat_id": -10000000000,
  "tg_bot_username": "@bot",
  "tg_api_id": "00000",
  "tg_api_hash": "00000000000000000000000000",
  "sheet_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sheet_name": "sheet",
  "links_regex": ""
}
```

|      البيانات       |                             معلومات                             |                                                                                    ملاحظات                                                                                     |
|:-------------------:|:---------------------------------------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    tg_bot_token     |            التوكن الخاص بواجهة برمجة تليجرام للبوتات            |                                                                                     إجباري                                                                                     |
|    tg_bot_admins    |                    قائمة معرفات مشرفي البوت                     |                                                                                     إجباري                                                                                     |
| tg_feedback_chat_id | معرف المحادثة التي سيرسل لها الملفات ورسائل التواصل مع المشرفين |                                                                                     إجباري                                                                                     |
|   tg_bot_username   |                    اسم المستخدم الخاص بالبوت                    |                                                                         تحتاجه أداة تحويل الروابط فقط                                                                          |
|      tg_api_id      |             معرف واجهة برمجة تليجرام للحساب الشخصي              |                                                                         تحتاجه أداة تحويل الروابط فقط                                                                          |
|     tg_api_hash     |         الهاش الخاص بواجهة برمجة تليجرام للحساب الشخصي          |                                                                         تحتاجه أداة تحويل الروابط فقط                                                                          |
|      sheet_id       |              معرف Google Sheet الخاصة بمواد البوت               |                                                                                     إجباري                                                                                     |
|     sheet_name      |                  اسم Google Sheet التي ستستخدم                  | إجباري<br />يمكن الاستعانة بهذا [النموذج](https://docs.google.com/spreadsheets/d/1o2016c9JQDROnhAhveKq70pF07_FozozP2xF7ekijTM/edit?usp=sharing) لمعرفة كيفية ملء بيانات المواد |
|     links_regex     |            تعبير regex المستخدم في البحث عن الروابط             |                                                       تحتاجه أداة تحويل الروابط فقط<br />مثال: "https://t.me/channel/.*"                                                       |

## تشغيل البوت

- استخدم اﻷمر التالي لبدء البوت باستخدام دوكر:

 ```bash
  docker-compose up --build -d
 ```

### تشغيل البوت بدون دوكر

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

## استخدام أداة تحويل روابط ملفات تليجرام إلى معرفات ملفات

- أولا تأكد من تشغيل البوت بشكل سليم وأن معرف حساب مشرف واحد على الأقل موجود في ملف التهيئة (وهو نفس الحساب الذي سيستخدم
  في أداة تحويل الروابط).

- تأكد أيضا من تثبيت الاعتماديات الاختيارية في حال استخدمت poetry في الخطوات السابقة.

  ```bash
  poetry install --extras "Pyrogram TgCrypto convopyro"
  ```

- شغل اﻷداة باستخدام اﻷمر وسجل الدخول إلى حساب تليجرام المستخدم في اﻷتمتة والذي يجب أن يكون له وصول إلى روابط الملفات
  الموجودة في Google Sheet

  ```bash
  python3 links_to_ids.py
  ```

- ستقوم اﻷداة بقراءة الروابط واستبدالها ب file id الخاص بكل ملف وكذلك إضافة وصف الملف إذا وجد حتى يستخدم عند إرسال
  الملفات للمستخدمين.

## معلومات تقنية

يستخدم البوت

- [Python 3.10](https://python.org/)
- [Docker](https://www.docker.com/)

ومكتبات بايثون

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot/)
- [python-telegram-bot-pagination](https://github.com/ksinn/python-telegram-bot-pagination)
- [https://github.com/burnash/gspread](https://github.com/burnash/gspread)
- [gspread-pandas](https://github.com/aiguofer/gspread-pandas)

وتستخدم أداة تحويل الروابط مكتبات

- [Pyrogram](https://github.com/pyrogram/pyrogram)
- [convopyro](https://github.com/Ripeey/Conversation-Pyrogram)
