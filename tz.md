# Kassa App Backend Documentation (Django & PostgreSQL)

Ushbu hujjat **Kassa App** ilovasi uchun backend tizimini loyihalash va amalga oshirish bo'yicha to'liq ko'rsatmalarni o'z ichiga oladi.

## 1. Texnologiyalar Steki

- **Language:** Python 3.12+
- **Framework:** Django 5.0+ & Django REST Framework (DRF)
- **Database:** PostgreSQL 16+
- **Auth:** JWT (SimpleJWT) - Access & Refresh tokens
- **Deployment:** Docker & Docker Compose

## 2. Ma'lumotlar Bazasi Modellar (Models)

### 2.1. Foydalanuvchi va Filial (Auth & Warehouse)

- **User:** Standart Django `User` modeli (`django.contrib.auth.models.User`). Faqat `username` va `password` maydonlari ishlatiladi.
- **Warehouse:** Filiallar ro'yxati (masalan: "Asosiy ombor", "Chilonzor filiali").

  - `name` (CharField)
  - `address` (TextField, optional)

### 2.2. Kundalik Hisobot (DailyReport)

Har bir hisobot ma'lum bir sana va omborga tegishli bo'ladi.

- `date` (DateField)
- `warehouse` (ForeignKey to Warehouse)
- `gross_sales` (DecimalField) - Umumiy savdo (qaytarishlarsiz)
- `returns_amount` (DecimalField) - Qaytarilgan mahsulotlar summasi
- `submitted_cash` (DecimalField) - Topshirilgan naqd pul
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### 2.3. To'lov Turlari (PaymentEntry)

- `report` (ForeignKey to DailyReport)
- `payment_type` (ChoiceField: Uzcard, Humo, Click, TransferClick)
- `amount` (DecimalField)

### 2.4. Muddatli To'lovlar (InstallmentItem)

- `report` (ForeignKey to DailyReport)
- `provider` (ChoiceField: Uzum, Alif)
- `months` (IntegerField: 3, 6, 12)
- `amount` (DecimalField)
- `commission` (DecimalField)

### 2.5. Xarajatlar (Expense)

- `report` (ForeignKey to DailyReport)
- `category` (CharField: "Хоз.товары", "Lanch", va h.k.)
- `amount` (DecimalField)
- `comment` (TextField)
- `employee_name` (CharField, optional)

### 2.6. Qarzlar va To'lovlar (Debt & DebtRepayment)

- **Debt:**

  - `report` (ForeignKey to DailyReport)
  - `client_name` (CharField)
  - `phone_number` (CharField, optional)
  - `amount` (DecimalField)
  - `date` (DateField)
- **DebtRepayment:** (Qaytarilgan qarzlar)

  - `report` (ForeignKey to DailyReport)
  - `client_name` (CharField)
  - `amount` (DecimalField)
  - `date` (DateField)

---

## 3. API Endpoints

### 3.1. Autentifikatsiya (JWT)

- `POST /api/v1/auth/login/`: Username va Password orqali login qilish. JSON qaytadi: `{access, refresh}`.
- `POST /api/v1/auth/refresh/`: Refresh token yuboriladi, yangi Access token qaytadi.
- `GET /api/v1/auth/profile/`: Joriy foydalanuvchi ma'lumotlari.

### 3.2. Hisobotlar (Reports)

- `GET /api/v1/reports/`: Filtrlangan hisobotlar ro'yxati (startDate, endDate, warehouse).
- `POST /api/v1/reports/sync/`: Kunlik hisobotni saqlash yoki yangilash.

**Payload Example:**

```json

{

"date":"2026-04-30",

"warehouse_id":1,

"gross_sales":65255500,

"returns_amount":5000000,

"submitted_cash":0,

"payments":[

{"type":"Uzcard","amount":1200000},

{"type":"Humo","amount":800000}

],

"installments":[

{"provider":"Uzum","months":6,"amount":1500000,"commission":150000}

],

"expenses":[

{"category":"Хоз.товары","amount":1747000,"comment":"Tavsif"}

],

"debts":[

{"client_name":"Alisher","amount":2500000,"date":"2026-04-30"}

],

"debt_repayments":[

{"client_name":"Sardor","amount":1448000,"date":"2026-04-30"}

]

}

```

- `GET /api/v1/reports/{id}/`: Bitta kunlik hisobotning barcha detallari.

### 3.3. Malumotnomalar (References)

- `GET /api/v1/warehouses/`: Filiallar ro'yxati.
- `GET /api/v1/expense-categories/`: Xarajat kategoriyalari ro'yxati.

---

## 4. Docker Konfiguratsiyasi

### 4.1. Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
```

### 4.2. docker-compose.yml

```yaml
services:
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=kassa_db
      - POSTGRES_USER=kassa_user
      - POSTGRES_PASSWORD=kassa_secret

  backend:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 core.wsgi:application
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
```

---

## 5. Implementatsiya bo'yicha ko'rsatmalar

1. **Transaction Management:** `reports/sync/` endpointida barcha bog'liq modellarni (Expenses, Payments, va h.k.) bitta atomik tranzaksiya ichida saqlang (`@transaction.atomic`).
2. **Permission Handling:** Barcha endpointlar `IsAuthenticated` bo'lishi shart.
3. **Environment Variables:** `SECRET_KEY`, `DATABASE_URL` va boshqa maxfiy qiymatlar `.env` faylida saqlanishi va `python-decouple` yoki `django-environ` orqali o'qilishi kerak.
3. **Validation:** Summalar musbat bo'lishi, sanalar to'g'ri formatda bo'lishini tekshirish (DRF Serializers yordamida).
4. **Calculations:**`ReportAmount` (Kassa qoldig'i) backend'da quyidagi formula bo'yicha tekshirilishi kerak:

`CalculatedCash = TotalSales - DigitalPaymentsSum`

`FinalAmount = CalculatedCash - ExpensesSum - DebtSum + DebtRepaidSum`

---

## 6. Frontend bilan integratsiya

Frontend `localStorage` dagi state'larni har safar "Save" tugmasi bosilganda `POST /api/v1/reports/sync/` ga yuboradi. Agar o'sha sana va ombor uchun ma'lumot bo'lsa, u yangilanadi (Update), aks holda yangi yaratiladi (Create).
