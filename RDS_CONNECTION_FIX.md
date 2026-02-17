# ⚠️ RDS Connection Slots Full - Solution

## ปัญหา
```
FATAL: remaining connection slots are reserved for roles with privileges of the "rds_reserved" role"
```

RDS มี connections เต็มแล้ว (max_connections limit)

## ✅ วิธีแก้ (3 วิธี)

### วิธีที่ 1: เพิ่ม max_connections (แนะนำ)

1. เข้า AWS Console → RDS → Parameter Groups
2. สร้าง Parameter Group ใหม่หรือแก้ไขที่มีอยู่
3. แก้ไข `max_connections`:
   ```
   max_connections = 100  (เพิ่มจาก default ~20)
   ```
4. Apply ไปที่ RDS instance
5. Reboot RDS instance

### วิธีที่ 2: ปิด Connections ที่ค้าง

```bash
python cleanup_rds.py
```

หรือใช้ SQL:
```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'postgres'
AND usename = 'postgres'
AND pid <> pg_backend_pid()
AND state = 'idle';
```

### วิธีที่ 3: ใช้ Connection Pooling (ทำแล้ว)

ระบบใช้ `SimpleConnectionPool` แล้ว:
- Min connections: 1
- Max connections: 3
- Auto close connections

## 🔍 ตรวจสอบ Connections

```bash
# ดู active connections
psql -h your-rds-host \
     -U postgres -d postgres -c \
     "SELECT count(*) FROM pg_stat_activity WHERE usename='postgres';"
```

## 💡 Best Practices

1. **ใช้ Connection Pooling** ✅ (ทำแล้ว)
2. **ปิด connections ทุกครั้ง** ✅ (ทำแล้ว)
3. **เพิ่ม max_connections** ⚠️ (ต้องทำที่ AWS)
4. **ใช้ RDS Proxy** (สำหรับ production)

## 🚀 RDS Proxy (Production)

สำหรับ production ควรใช้ RDS Proxy:
- จัดการ connection pooling อัตโนมัติ
- รองรับ connections หลายพัน
- Failover อัตโนมัติ

```python
# ใน .env
DB_HOST=your-rds-proxy-endpoint.proxy-xxx.region.rds.amazonaws.com
```

## 📊 RDS Instance Size

| Instance | max_connections | RAM |
|----------|----------------|-----|
| db.t3.micro | ~85 | 1GB |
| db.t3.small | ~150 | 2GB |
| db.t3.medium | ~300 | 4GB |

**แนะนำ:** อัพเกรดเป็น db.t3.small หรือใหญ่กว่า

## 🔧 Quick Fix

```bash
# 1. ปิด connections ที่ค้าง
python cleanup_rds.py

# 2. ทดสอบใหม่
python test_rds.py

# 3. รันแอป
python local_app.py
```

## 📞 ติดต่อ AWS Support

หากยังแก้ไม่ได้:
1. เปิด AWS Support ticket
2. ขอเพิ่ม max_connections
3. หรือขอ upgrade instance size

---

**หมายเหตุ:** ระบบใช้ connection pooling แล้ว (max 3 connections) แต่ RDS อาจมี connections เก่าค้างอยู่จากการทดสอบก่อนหน้า
