# DO'KON ERP — Tenant API Hujjatlari

## Umumiy ma'lumot

Barcha API'lari `/api/tenant/` prefix bilan boshlanadi.
Autentifikatsiya: `Authorization: Bearer <token>` header orqali.

---

## 1. Profil

### `GET /api/tenant/profile/`
Firma profilini olish.

**Response:**
```json
{
  "id": 1,
  "name": "Oazis Market",
  "phone": "+998901234567",
  "currency": "UZS",
  "timezone": "Asia/Tashkent",
  "language": "uz",
  "user_count": 5,
  "product_count": 120,
  "total_revenue": 12500000
}
```

### `PUT /api/tenant/profile/`
Firma profilini yangilash.

**Request:**
```json
{
  "name": "Yangi nom",
  "phone": "+998901234567"
}
```

---

## 2. Sozlamalar

### `GET /api/tenant/settings/`
Sozlamalarni olish.

### `PUT /api/tenant/settings/`
Sozlamalarni yangilash.

**Request:**
```json
{
  "currency": "USD",
  "timezone": "Asia/Tashkent",
  "language": "ru"
}
```

---

## 3. Dashboard

### `GET /api/tenant/dashboard/`
Statistik ma'lumotlar.

**Response:**
```json
{
  "company": "Oazis Market",
  "today": {"count": 12, "total": 850000},
  "week": {"count": 85, "total": 5200000},
  "month": {"count": 320, "total": 18500000},
  "totals": {
    "products": 150,
    "categories": 25,
    "customers": 80,
    "users": 5
  }
}
```

---

## 4. Foydalanuvchilar

### `GET /api/tenant/users/`
Foydalanuvchilar ro'yxati.

### `POST /api/tenant/quick-create/`
Yangi foydalanuvchi yaratish.

**Request:**
```json
{
  "username": "kassa3",
  "password": "123456",
  "role": "CASHIER",
  "branch_id": 1
}
```

### `DELETE /api/tenant/users/<id>/`
Foydalanuvchini o'chirish.

---

## 5. Taklif

### `POST /api/tenant/send-invitation/`
Email orqali taklif yuborish.

**Request:**
```json
{
  "email": "user@example.com",
  "role": "CASHIER",
  "branch_id": 1
}
```

---

## 6. Obuna

### `GET /api/tenant/billing/`
Obuna ma'lumotlari.

**Response:**
```json
{
  "is_active": true,
  "subscription_end_date": "2026-10-05",
  "monthly_fee": 200000,
  "days_remaining": 30,
  "is_valid": true,
  "monthly_revenue": 5200000
}
```

### `POST /api/tenant/billing/extend/`
Obunani uzaytirish.

**Request:**
```json
{
  "days": 30
}
```

### `GET /api/tenant/billing/history/`
To'lov tarixi.

### `POST /api/tenant/billing/toggle/`
Firmani to'xtatish/faollashtirish.

---

## 7. Ogohlantirishlar

### `GET /api/tenant/notifications/`
Barcha ogohlantirishlar.

**Response:**
```json
{
  "count": 3,
  "alerts": [
    {
      "type": "warning",
      "title": "Obuna tugayapti!",
      "message": "Obunangiz 7 kundan keyin tugaydi.",
      "action": "/api/tenant/billing/extend/"
    }
  ]
}
```

### `GET /api/tenant/alerts-summary/`
Qisqacha hisobot.

---

## 8. Audit Log

### `GET /api/tenant/audit-log/`
Amallar tarixi.

**Query params:** `?action=CREATE&model=product`

---

## 9. Export

### `GET /api/tenant/export/products/`
Mahsulotlarni CSV formatida export qilish.

### `GET /api/tenant/export/sales/`
Savdolarni CSV formatida export qilish.

### `GET /api/tenant/export/all/`
Barcha ma'lumotlarni JSON formatida backup qilish.

---

## 10. Filiallar

### `GET /api/tenant/branches/`
Filiallar ro'yxati.
