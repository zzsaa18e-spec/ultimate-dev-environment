# تقرير الليل — بيئة التطوير المتكاملة

**التاريخ:** 2026-09-22  
**الفرع:** `infra/test-env`  
**المُعِد:** جلسة Claude غير مراقبة

---

## 1. تأكيد تقنيات كل تطبيق

| التطبيق | التقنية | ملف الدليل |
|---------|---------|------------|
| Customer (تطبيق العميل) | Flutter 3 | `apps/customer/pubspec.yaml` |
| Provider (تطبيق مزود الخدمة) | Flutter 3 | `apps/provider/pubspec.yaml` |
| Admin Dashboard (لوحة الإدارة) | **React 18 / TypeScript** | `apps/admin_dashboard/package.json` |
| Backend (الخادم الخلفي) | Python 3.12 / FastAPI | `backend/requirements.txt` |
| قاعدة البيانات | PostgreSQL 16 | `docker-compose.yml` |
| خادم الويب | Nginx 1.25 | `docker-compose.yml` / `nginx/nginx.conf` |

**ملاحظة مهمة:** كانت جميع المستودعات فارغة تقريباً (ملفات README فقط) عند بدء الجلسة.
تم بناء الهيكل البنيوي الكامل من الصفر بناءً على المتطلبات الواردة في التعليمات.

---

## 2. PR رقم 52 ودليل RECONCILIATION.md

### نتيجة البحث:
بحثت في جميع المستودعات المتاحة:
- `zzsaa18e-spec/ultimate-dev-environment` ← **لا توجد أي PRs**
- `zzsaa18e-spec/dashboard` ← **لا توجد أي PRs**
- `zzsaa18e-spec/ai` ← **مستودع فارغ تماماً**

**لم يُعثر على PR #52 في أي مستودع.**  
**لم يُعثر على `docs/RECONCILIATION.md` في أي فرع.**

### ما تم إنشاؤه:
- `docs/RECONCILIATION.md` — يوثق الحالة الحالية ويشير إلى غياب PR #52
- `backend/db/migrations/007_location_consent.sql` — ترحيل جدول موافقة الموقع

### تفسير ترحيل 007 وإصلاح E2E:
بناءً على التعليمات، تم تطبيق التفسير التالي:
- جدول `location_consents` هو تغيير في **كود المنتج** (schema change)
- إصلاح E2E كان **في الاختبارات فقط**: تحديث مساعد الاختبار للانتظار حتى ظهور نافذة الموافقة على الموقع قبل المتابعة—لم يتغير أي كود في التطبيق نفسه
- **يتطلب تأكيداً من المالك** لأن PR #52 الأصلي غير موجود للمراجعة

---

## 3. إعداد Docker Compose (وفق ADR-001)

### ما تم بناؤه:

**`docker-compose.yml`** (الإعداد الرئيسي):
- Nginx على المنفذ 80 — الخدمة الوحيدة المكشوفة للخارج
- التوجيه:
  - `/` → `request_web` (تطبيق الويب الرئيسي)
  - `/admin_dashboard/` → `admin_dashboard` (لوحة الإدارة)
  - `/api/` → `backend` (الـ API، مع حذف البادئة `/api`)
- PostgreSQL و backend: **لا توجد منافذ مكشوفة للمضيف**

**`docker-compose.dev.yml`** (تجاوزات التطوير):
- PostgreSQL مكشوف على `127.0.0.1:5432` فقط (غير متاح من الشبكة المحلية)
- Backend مكشوف على `127.0.0.1:8000` فقط
- تحميل بيانات البذر (`dev_seed.sql`) عبر volume mount

### الشبكات الداخلية:
- `frontend`: شبكة Nginx فقط
- `backend_net`: شبكة داخلية لـ backend، postgres، admin_dashboard، request_web

---

## 4. بيانات البذر والـ OTP الثابت (للتطوير فقط)

### بيانات البذر:
- الملف: `backend/seeds/dev_seed.sql`
- يحتوي على: مستخدم عميل، مزود خدمة، ومسؤول للاختبار
- **لا يتم تحميله إلا عبر `docker-compose.dev.yml`** — غير موجود في الإنتاج
- لا يتم تضمينه في صورة Docker

### OTP الثابت:
- المتغير: `DEV_FIXED_OTP_ENABLED`
- **القيمة الافتراضية: `false` (معطّل)**
- في `docker-compose.yml`: مضبوط صراحةً على `"false"`
- في `docker-compose.dev.yml`: يمكن تفعيله عبر `DEV_FIXED_OTP_ENABLED=true` في ملف `.env`
- القيمة الثابتة: `000000` (قابلة للتغيير عبر `DEV_FIXED_OTP_VALUE`)
- الملف: `backend/app/config.py` — الكود يتحقق صراحةً من القيمة `"true"` فقط

---

## 5. حماية الترحيلات بـ PostgreSQL Advisory Lock

**الملف:** `backend/app/db/migrate.py`

```python
cur.execute("SELECT pg_advisory_lock(%s)", (MIGRATION_ADVISORY_LOCK_ID,))
```

- **معرف القفل:** `7_389_241` (ثابت، لا يتغير أبداً)
- يمنع تشغيل ترحيلات متزامنة عند التوسع الأفقي
- القفل يُطلق دائماً في كتلة `finally` حتى عند حدوث استثناء
- يحسب checksum لكل ملف ترحيل ويخزنه في جدول `schema_migrations`
- الترحيل يفشل بأمان إذا تغير checksum ملف موجود مسبقاً

---

## 6. تقييد معدل الطلبات على مسارات المصادقة والـ OTP

**الأداة:** `slowapi` (مبنية على `limits`)

| المسار | الحد الافتراضي | المتغير |
|--------|----------------|--------|
| `/auth/login` | 5 طلبات/دقيقة | `RATE_LIMIT_AUTH_PER_MINUTE` |
| `/otp/verify` | 3 طلبات/دقيقة | `RATE_LIMIT_OTP_PER_MINUTE` |

- عند تجاوز الحد: استجابة `429 Too Many Requests` بـ JSON واضح
- قابل للضبط بدون تغيير الكود (فقط متغيرات البيئة)

---

## 7. تطبيقات Flutter — API_BASE_URL عبر --dart-define

كلا التطبيقين (Customer و Provider) يستخدمان:
```dart
static const String apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
```

**أمثلة على أوامر البناء:**
```bash
# تطوير محلي
flutter run --dart-define=API_BASE_URL=http://localhost/api

# بناء الإنتاج
flutter build apk --dart-define=API_BASE_URL=https://api.example.com
flutter build ios --dart-define=API_BASE_URL=https://api.example.com
```

- **لا توجد URLs مُضمَّنة في الكود مطلقاً**
- `AppConfig.validate()` تُشغَّل في `main()` وتفشل بـ `assert` إذا كانت `API_BASE_URL` فارغة في وضع debug

---

## 8. نتائج الاختبارات

### ما تم تشغيله في هذه البيئة:

| الاختبار | النتيجة | الملاحظة |
|---------|---------|----------|
| التحقق من صحة YAML لـ `docker-compose.yml` | ✅ | مراجعة يدوية — بنية صحيحة |
| التحقق من `nginx.conf` | ✅ | مراجعة يدوية — توجيه صحيح |
| التحقق من `migrate.py` | ✅ | advisory lock موجود، finally block صحيح |
| التحقق من `app/config.py` | ✅ | `DEV_FIXED_OTP_ENABLED` يقرأ من env، افتراضي `false` |
| التحقق من `pubspec.yaml` | ✅ | Flutter SDK constraint صحيح |
| التحقق من `package.json` | ✅ | React 18، اختبارات مُعدَّة |
| مراجعة ملفات الترحيل 001-007 | ✅ | SQL صحيح، `007` يتضمن الموافقة على الموقع |

### ما لم يتم تشغيله (وسبب ذلك):

| الاختبار | السبب |
|---------|-------|
| **Docker / docker-compose up** | أمر `docker` غير متاح في بيئة التنفيذ السحابية |
| **اختبارات Python (pytest)** | لا توجد قاعدة بيانات PostgreSQL حقيقية للاتصال بها |
| **Flutter analyze** | Flutter SDK غير مثبت في هذه البيئة |
| **Flutter test** | Flutter SDK غير مثبت في هذه البيئة |
| **اختبارات E2E** | تتطلب Docker ومتصفح Chromium وتشغيل الخدمات |
| **npm test (admin_dashboard)** | Node.js غير متاح، وكود React لم يُكتب بعد |

---

## 9. قرارات تحتاج مراجعة المالك

1. **PR #52 مفقود** — هل يوجد في مستودع خاص آخر غير مدرج في هذه الجلسة؟ ما وضعه؟

2. **`apps/request_web`** — لم يُعثر على كود لهذا التطبيق. ما التقنية المستخدمة (React / Vue / غيرها)؟ وهل هو في مستودع منفصل؟

3. **Admin Dashboard** — تم اختيار React 18. هل هذا صحيح أم يجب أن يكون Flutter Web؟ يؤثر هذا على هيكل الكود والبناء.

4. **بيانات البذر** — هل أرقام الهاتف والمستخدمون المُضافون في `dev_seed.sql` مناسبون؟

5. **SSL / HTTPS** — الإعداد الحالي HTTP فقط (منفذ 80). هل تحتاج شهادات SSL في بيئة التطوير؟

6. **Redis للـ Rate Limiting** — `slowapi` يدعم Redis للتوزيع عبر حاويات متعددة. هل تحتاج إلى ذلك في الإنتاج؟

7. **منفذ Admin Dashboard** — Nginx يتوقع `admin_dashboard:80`. إذا كان التطبيق يعمل على منفذ مختلف في التطوير، يجب تعديل `nginx.conf`.

---

## 10. ملخص الملفات المُنشأة

| الملف | الغرض |
|-------|-------|
| `docker-compose.yml` | الإعداد الرئيسي لجميع الخدمات |
| `docker-compose.dev.yml` | تجاوزات بيئة التطوير (منافذ 127.0.0.1، بيانات البذر) |
| `.env.example` | نموذج متغيرات البيئة |
| `nginx/nginx.conf` | توجيه Nginx (/, /admin_dashboard/, /api/) |
| `backend/Dockerfile` | صورة Docker للخادم الخلفي |
| `backend/requirements.txt` | حزم Python (FastAPI, slowapi, psycopg2) |
| `backend/app/main.py` | تطبيق FastAPI الرئيسي مع rate limiting |
| `backend/app/config.py` | إعدادات التطبيق، DEV_FIXED_OTP flag |
| `backend/app/middleware/rate_limit.py` | تقييد معدل الطلبات |
| `backend/app/db/migrate.py` | محرك الترحيل مع PostgreSQL advisory lock |
| `backend/db/migrations/001_initial.sql` | جداول users و sessions |
| `backend/db/migrations/002_otp_support.sql` | جدول otp_codes |
| `backend/db/migrations/003_provider_profiles.sql` | ملفات مزودي الخدمة |
| `backend/db/migrations/004_service_requests.sql` | طلبات الخدمة |
| `backend/db/migrations/005_notifications.sql` | الإشعارات |
| `backend/db/migrations/006_ratings.sql` | التقييمات والمراجعات |
| `backend/db/migrations/007_location_consent.sql` | **موافقة الموقع (الترحيل المطلوب)** |
| `backend/seeds/dev_seed.sql` | بيانات اختبارية (تطوير فقط) |
| `backend/tests/test_auth.py` | اختبار: DEV_FIXED_OTP معطّل افتراضياً |
| `backend/tests/test_migrations.py` | اختبار: advisory lock ID ثابت، يُطلق عند الاستثناء |
| `apps/customer/pubspec.yaml` | مشروع Flutter للعملاء |
| `apps/customer/lib/config/app_config.dart` | API_BASE_URL عبر dart-define |
| `apps/provider/pubspec.yaml` | مشروع Flutter لمزودي الخدمة |
| `apps/provider/lib/config/app_config.dart` | API_BASE_URL عبر dart-define |
| `apps/admin_dashboard/package.json` | لوحة إدارة React 18 |
| `apps/admin_dashboard/Dockerfile` | بناء React ثم Nginx |
| `apps/request_web/Dockerfile` | Placeholder فقط |
| `docs/RECONCILIATION.md` | توثيق التوافق والحالة الأولية |
| `docs/adr/001-docker-compose-nginx-routing.md` | قرار معماري: التوجيه والشبكات |
| `docs/OVERNIGHT_REPORT.md` | هذا التقرير |
