# 🇮🇷 IRANIAN HOSTING - COST ANALYSIS & SETUP GUIDE

## 💰 **COST COMPARISON: RENDER vs IRANIAN SERVERS**

### **Render (International):**
```
Web Service:        $85/month
PostgreSQL:         $20/month
SendGrid:           $90/month
Redis:              $10/month
Monitoring:         $26/month
────────────────────────────────
TOTAL:              $231/month
```

### **Iranian Servers (Estimated):**
```
VPS (4GB RAM, 2 CPU):    $15-30/month (or 500K-1M Toman)
PostgreSQL:              Included (on VPS)
Email Service:          $5-10/month (or free with SMTP)
Redis:                  Included (on VPS)
Monitoring:             Free (self-hosted)
────────────────────────────────
TOTAL:                  $20-40/month (or 700K-1.4M Toman)
```

**Savings: 90% cheaper!** 🎉

---

## 🎯 **IRANIAN HOSTING OPTIONS**

### **Option 1: Iranian VPS Providers**

#### **1. Iran Server (ایران سرور)**
```
VPS Plans:
├─ Basic: 2GB RAM → 400K Toman/month (~$10)
├─ Standard: 4GB RAM → 800K Toman/month (~$20)
└─ Pro: 8GB RAM → 1.5M Toman/month (~$36)

Features:
✅ Local support
✅ Iranian payment methods
✅ Good uptime
```

#### **2. Pars Data (پارس دیتا)**
```
VPS Plans:
├─ Starter: 2GB RAM → 450K Toman/month (~$11)
└─ Standard: 4GB RAM → 900K Toman/month (~$22)

Features:
✅ Established provider
✅ Good infrastructure
```

#### **3. Nik Server (نیک سرور)**
```
VPS Plans:
├─ Basic: 2GB RAM → 350K Toman/month (~$8)
└─ Standard: 4GB RAM → 700K Toman/month (~$17)

Features:
✅ Very affordable
✅ Good for startups
```

---

## 💡 **RECOMMENDED SETUP FOR 100K USERS (IRANIAN SERVER)**

### **Infrastructure:**
```
VPS: 4GB RAM, 2 CPU
├─ Cost: 1M Toman/month (~$24)
├─ OS: Ubuntu 22.04 LTS
├─ Web: Nginx + Gunicorn
├─ Database: PostgreSQL (on same VPS)
├─ Cache: Redis (on same VPS)
└─ Email: SMTP (free) or Iranian email service

Total: ~$24/month (vs $231 on Render!)
```

### **Email Service Options:**

#### **Option A: Free SMTP (Gmail/Outlook)**
```
Cost: $0/month
Limit: 500 emails/day (Gmail free)
Status: ✅ Good for 5K-10K users
```

#### **Option B: Iranian Email Service**
```
Providers:
├─ Pars Data Mail: 80K Toman/month (~$2)
├─ Iran Server Mail: 90K Toman/month (~$2.25)
└─ Custom SMTP: Free (if you have server)

Cost: $0-3/month
```

#### **Option C: Self-Hosted Email (Postfix)**
```
Cost: $0/month
Setup: Complex but free
Status: ⚠️  Not recommended (deliverability issues)
```

---

## 🔧 **DEPLOYMENT GUIDE FOR IRANIAN VPS**

### **Step 1: Server Setup**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 4. Install Redis
sudo apt install redis-server -y

# 5. Install Nginx
sudo apt install nginx -y

# 6. Install Git
sudo apt install git -y
```

### **Step 2: Database Setup**

```bash
# Create database user
sudo -u postgres psql
CREATE USER myshop_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE myshop_db OWNER myshop_user;
\q

# Configure PostgreSQL
sudo nano /etc/postgresql/14/main/postgresql.conf
# Set: max_connections = 100
# Set: shared_buffers = 1GB

sudo systemctl restart postgresql
```

### **Step 3: Redis Setup**

```bash
# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: maxmemory 512mb
# Set: maxmemory-policy allkeys-lru

sudo systemctl restart redis
```

### **Step 4: Deploy Django App**

```bash
# Clone your repository
cd /var/www
git clone https://github.com/your-username/myshop-backend.git
cd myshop-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### **Step 5: Gunicorn Setup**

```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn service
sudo nano /etc/systemd/system/myshop.service
```

**File content:**
```ini
[Unit]
Description=MyShop Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/myshop-backend
ExecStart=/var/www/myshop-backend/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    myshop.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start myshop
sudo systemctl enable myshop
```

### **Step 6: Nginx Configuration**

```bash
sudo nano /etc/nginx/sites-available/myshop
```

**File content:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/myshop-backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/myshop-backend/media/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/myshop /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 7: SSL Certificate (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 📊 **COST BREAKDOWN: IRANIAN HOSTING**

### **Monthly Costs:**

```
VPS (4GB RAM, 2 CPU):        1M Toman (~$24)
Domain (.ir):                50K Toman/year (~$1.20/month)
Email Service (optional):    100K Toman (~$2.50)
────────────────────────────────────────────
TOTAL:                        ~$27.70/month
                              (vs $231 on Render!)

Savings: 88% cheaper! 🎉
```

### **For 100K Users:**
```
Cost per user: $0.000277/month
              (vs $0.00231 on Render)

10x cheaper per user!
```

---

## ⚡ **PERFORMANCE COMPARISON**

### **Render (International):**
```
Iranian Users:
├─ Latency: 200-500ms (slow)
├─ Speed: Moderate
└─ Experience: ⚠️  Slower for Iranian users
```

### **Iranian Server:**
```
Iranian Users:
├─ Latency: 10-50ms (very fast!)
├─ Speed: Excellent
└─ Experience: ✅ Much faster for Iranian users
```

**Iranian users will have MUCH better experience on Iranian servers!** 🚀

---

## 🔒 **SECURITY CONSIDERATIONS**

### **For Iranian Servers:**

1. **Firewall Setup:**
```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

2. **Fail2Ban (Prevent Brute Force):**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

3. **Regular Backups:**
```bash
# Create backup script
sudo nano /usr/local/bin/backup-myshop.sh
```

**Backup script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/myshop"

# Backup database
pg_dump -U myshop_user myshop_db > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/myshop-backend/media/

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-myshop.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-myshop.sh
```

---

## 🎯 **OPTIMIZATION FOR IRANIAN SERVERS**

### **1. Database Optimization:**

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myshop_db',
        'USER': 'myshop_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### **2. Cache Configuration:**

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'myshop',
        'TIMEOUT': 3600,
    }
}
```

### **3. Static Files (CDN Optional):**

```python
# Use local storage (faster for Iranian users)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## 📋 **DEPLOYMENT CHECKLIST**

### **Server Setup:**
```
[ ] Choose VPS provider (Arvan, Iran Server, etc.)
[ ] Order VPS (4GB RAM, 2 CPU minimum)
[ ] Set up Ubuntu 22.04
[ ] Configure firewall
[ ] Install PostgreSQL
[ ] Install Redis
[ ] Install Nginx
[ ] Install Python 3.11
```

### **Application Deployment:**
```
[ ] Clone repository
[ ] Set up virtual environment
[ ] Install dependencies
[ ] Configure settings.py
[ ] Run migrations
[ ] Collect static files
[ ] Set up Gunicorn
[ ] Configure Nginx
[ ] Set up SSL certificate
```

### **Security:**
```
[ ] Configure firewall
[ ] Set up Fail2Ban
[ ] Configure backups
[ ] Set up monitoring
[ ] Test disaster recovery
```

### **Email:**
```
[ ] Choose email service (Arvan Mail or free SMTP)
[ ] Configure SMTP settings
[ ] Test email delivery
```

---

## 💰 **FINAL COST COMPARISON**

### **Render (International):**
```
Monthly: $231
Yearly: $2,772
Per 100K users: $0.00231/user/month
```

### **Iranian Server:**
```
Monthly: 1.1M Toman (~$27)
Yearly: 13.2M Toman (~$324)
Per 100K users: $0.00027/user/month

Savings: 88% cheaper!
```

---

## ✅ **RECOMMENDATIONS**

### **For Iranian Users:**
1. ✅ **Use Iranian VPS** (much cheaper + faster)
2. ✅ **Iran Server, Pars Data, or Nik Server** (reliable providers)
3. ✅ **4GB RAM, 2 CPU** (sufficient for 100K users)
4. ✅ **Free SMTP** (Gmail) or Pars Data Mail ($2/month)
5. ✅ **Self-hosted Redis** (included in VPS)

### **Total Cost:**
```
VPS: 1M Toman/month (~$24)
Email: 100K Toman/month (~$2.50) [optional]
────────────────────────────────
TOTAL: ~$27/month

vs Render: $231/month

You save: $204/month (88% cheaper!)
```

---

## 🚀 **NEXT STEPS**

1. **Choose VPS Provider:**
   - Iran Server (recommended)
   - Pars Data
   - Nik Server

2. **Order VPS:**
   - 4GB RAM, 2 CPU minimum
   - Ubuntu 22.04 LTS

3. **Follow Deployment Guide:**
   - Use the steps above
   - Test thoroughly
   - Monitor performance

4. **Set Up Email:**
   - Use Gmail SMTP (free, 500/day limit)
   - Or Arvan Mail ($2.50/month, unlimited)

---

## 🎉 **CONCLUSION**

**Iranian hosting is:**
- ✅ **88% cheaper** than Render
- ✅ **Much faster** for Iranian users
- ✅ **Better support** (Persian language)
- ✅ **Local payment** (Toman, no currency issues)
- ✅ **Perfect for 100K users** at $27/month

**You made the right choice!** 🇮🇷

---

**Need help setting up on Iranian server? I can guide you through the deployment!** 🚀

