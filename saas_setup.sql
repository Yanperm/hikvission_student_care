-- SaaS Database Schema
-- เพิ่มตารางสำหรับระบบ SaaS

-- 1. Plans Table (แพ็กเกจ)
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL, -- monthly, yearly
    max_students INTEGER NOT NULL,
    max_users INTEGER NOT NULL,
    features JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Subscriptions Table (การสมัครใช้งาน)
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    subscription_id VARCHAR(50) UNIQUE NOT NULL,
    school_id VARCHAR(50) NOT NULL,
    plan_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- active, expired, cancelled, trial
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id),
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
);

-- 3. Payments Table (ประวัติการชำระเงิน)
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(50) UNIQUE NOT NULL,
    school_id VARCHAR(50) NOT NULL,
    subscription_id VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'THB',
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) NOT NULL, -- pending, completed, failed, refunded
    transaction_id VARCHAR(200),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id)
);

-- 4. School Settings Table (การตั้งค่าโรงเรียน)
CREATE TABLE IF NOT EXISTS school_settings (
    id SERIAL PRIMARY KEY,
    school_id VARCHAR(50) UNIQUE NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    custom_domain VARCHAR(200),
    logo_url TEXT,
    primary_color VARCHAR(20) DEFAULT '#007aff',
    timezone VARCHAR(50) DEFAULT 'Asia/Bangkok',
    language VARCHAR(10) DEFAULT 'th',
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id)
);

-- 5. Usage Stats Table (สถิติการใช้งาน)
CREATE TABLE IF NOT EXISTS usage_stats (
    id SERIAL PRIMARY KEY,
    school_id VARCHAR(50) NOT NULL,
    stat_date DATE NOT NULL,
    total_students INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    total_attendance INTEGER DEFAULT 0,
    storage_used BIGINT DEFAULT 0, -- bytes
    api_calls INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id),
    UNIQUE(school_id, stat_date)
);

-- อัพเดท Schools Table
ALTER TABLE schools ADD COLUMN IF NOT EXISTS email VARCHAR(200);
ALTER TABLE schools ADD COLUMN IF NOT EXISTS subdomain VARCHAR(100);
ALTER TABLE schools ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP;
ALTER TABLE schools ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;

-- Insert Default Plans
INSERT INTO plans (plan_id, name, description, price, billing_cycle, max_students, max_users, features) VALUES
('FREE', 'ทดลองใช้ฟรี', 'ทดลองใช้ 30 วัน', 0, 'monthly', 50, 5, '{"line_notification": false, "reports": false, "support": "email"}'),
('BASIC', 'แพ็กเกจพื้นฐาน', 'เหมาะสำหรับโรงเรียนขนาดเล็ก', 990, 'monthly', 200, 10, '{"line_notification": true, "reports": true, "support": "email"}'),
('PRO', 'แพ็กเกจมืออาชีพ', 'เหมาะสำหรับโรงเรียนขนาดกลาง', 2990, 'monthly', 1000, 50, '{"line_notification": true, "reports": true, "ai_analytics": true, "support": "priority"}'),
('ENTERPRISE', 'แพ็กเกจองค์กร', 'ไม่จำกัดจำนวน', 9990, 'monthly', 999999, 999, '{"line_notification": true, "reports": true, "ai_analytics": true, "custom_domain": true, "support": "24/7"}')
ON CONFLICT (plan_id) DO NOTHING;
