# CSRF CTF Challenge - Project Structure

## 📁 Directory Structure

```
csrf-ctf/
├── app.py                          # Main Flask application
├── admin_bot.py                    # Admin bot with Selenium
├── admin_bot_playwright.py         # Admin bot with Playwright
├── admin_bot_simple.py             # Admin bot with requests (lightweight)
├── exploit_example.html            # Example exploit for reference
│
├── Dockerfile                      # Docker config with Selenium
├── Dockerfile.playwright           # Docker config with Playwright
├── Dockerfile.simple               # Docker config (lightweight, recommended)
│
├── docker-compose.yml              # Docker Compose for Selenium version
├── docker-compose.playwright.yml   # Docker Compose for Playwright version
├── docker-compose.simple.yml       # Docker Compose for simple version (recommended)
│
├── requirements.txt                # Python dependencies for Selenium
├── requirements.playwright.txt     # Python dependencies for Playwright
├── requirements.simple.txt         # Python dependencies for simple version
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template with navigation
│   ├── index.html                  # Landing page
│   ├── login.html                  # Login form
│   ├── register.html               # Registration form
│   ├── profile.html                # User profile page
│   ├── users.html                  # Users list page
│   └── report.html                 # Report URL form
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
├── SOLUTION.md                     # Solution guide (for instructors)
├── PROJECT_STRUCTURE.md            # This file
└── .gitignore                      # Git ignore rules
```

## 🔧 Core Files

### app.py
Main Flask application with the following endpoints:

- `GET /` - Landing page
- `GET/POST /register` - User registration
- `GET/POST /login` - User authentication
- `GET /logout` - Logout
- `GET /profile` - View own profile
- `POST /update_profile` - Update profile (VULNERABLE TO CSRF)
- `GET /users` - List all non-admin users
- `GET/POST /report` - Report URL to admin

**Key Features:**
- SQLite database for user storage
- Session-based authentication
- Admin user with flag in bio field
- No CSRF protection (intentional vulnerability)

### Admin Bots

Three implementations available:

#### admin_bot_simple.py (Recommended)
- Uses `requests` library
- Lightweight, no browser dependencies
- Works on all platforms including ARM (Mac M1/M2)
- Maintains session via cookies
- Follows redirects automatically

#### admin_bot_playwright.py
- Uses Playwright for browser automation
- Full JavaScript execution
- Requires x86_64 architecture
- More realistic admin behavior

#### admin_bot.py
- Uses Selenium with ChromeDriver
- Full browser automation
- Complex setup with Chrome dependencies
- Alternative to Playwright

### Templates

#### base.html
- Master template with CSS styling
- Navigation menu for authenticated users
- Gradient purple theme
- Responsive design

#### profile.html
- Displays username, role (if admin), bio, and website
- Form to update bio and website
- **CSRF vulnerability point** - no token validation

#### users.html
- Lists all non-admin users
- Shows username and website (if set)
- Students can view admin's updated profile here

#### report.html
- Form to submit URL to admin
- Admin bot will visit the submitted URL
- Key component for exploit delivery

## 🐳 Docker Configurations

### Recommended: docker-compose.simple.yml
```yaml
- Uses Dockerfile.simple
- Minimal dependencies (Flask + requests)
- Works on all architectures
- Fast build time (~5 seconds)
- Port 5000 exposed
```

### Alternative: docker-compose.playwright.yml
```yaml
- Uses Dockerfile.playwright
- Includes Playwright browser
- Requires x86_64 architecture
- Longer build time (~2 minutes)
- 2GB shared memory allocated
```

### Alternative: docker-compose.yml
```yaml
- Uses Dockerfile (Selenium)
- Includes Chrome and ChromeDriver
- Complex dependencies
- Longest build time
```

## 🗄️ Database Schema

### users table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,          -- SHA256 hashed
    bio TEXT DEFAULT '',
    website TEXT DEFAULT '',
    is_admin INTEGER DEFAULT 0
);
```

**Default Admin User:**
- Username: `admin`
- Password: `admin_secret_password_123` (hashed)
- Bio: `centralctf{csrf_1s_n0t_d3ad_yet}` (the flag)
- is_admin: `1`

## 🔐 Security Features (Intentionally Missing)

### CSRF Protection
- ❌ No CSRF tokens on forms
- ❌ No SameSite cookie attributes
- ❌ No Referer header validation
- ❌ No custom header requirements

### Session Management
- ✅ Secure session cookies (Flask default)
- ✅ Server-side sessions
- ❌ No session timeout
- ❌ No IP validation

## 🎯 Vulnerability Details

### CSRF in /update_profile

**Vulnerable Code:**
```python
@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    bio = request.form.get("bio", "")
    website = request.form.get("website", "")
    
    conn = get_db()
    conn.execute(
        "UPDATE users SET bio = ?, website = ? WHERE id = ?",
        (bio, website, session["user_id"]),
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for("profile"))
```

**Why it's vulnerable:**
1. Accepts POST requests without CSRF token validation
2. Uses session cookies (automatically sent by browser)
3. No origin/referer checking
4. Admin bot visits attacker-controlled URLs while authenticated

## 🚀 Deployment Options

### Option 1: Simple Version (Recommended)
```bash
docker-compose -f docker-compose.simple.yml up --build -d
```
- ✅ Works everywhere
- ✅ Fast deployment
- ✅ Minimal resources
- ⚠️ Admin bot doesn't execute JavaScript

### Option 2: Playwright Version
```bash
docker-compose -f docker-compose.playwright.yml up --build -d
```
- ✅ Full browser automation
- ✅ JavaScript execution
- ❌ x86_64 only
- ⚠️ Slower build

### Option 3: Manual Setup
```bash
pip install -r requirements.simple.txt
python app.py
```
- ✅ No Docker needed
- ✅ Easy debugging
- ⚠️ Manual dependency management

## 📊 Resource Requirements

### Simple Version
- **Memory:** ~50MB
- **CPU:** Minimal
- **Disk:** ~200MB (base image + app)
- **Build time:** ~10 seconds
- **Startup time:** <1 second

### Playwright Version
- **Memory:** ~500MB
- **CPU:** Moderate
- **Disk:** ~1.5GB (with Chromium)
- **Build time:** ~2 minutes
- **Startup time:** ~3 seconds

## 🔄 Data Flow

### Normal Profile Update
```
User Browser → POST /update_profile → Flask → SQLite → Redirect
```

### CSRF Attack Flow
```
1. Attacker creates malicious HTML page
2. Student reports URL via /report
3. Admin bot logs in as admin
4. Admin bot visits attacker's URL
5. Malicious page submits form to /update_profile
6. Admin's profile gets updated
7. Student views admin profile via /users
8. Flag is visible in admin's updated data
```

## 📝 Environment Variables

```bash
FLAG=centralctf{csrf_1s_n0t_d3ad_yet}  # The flag to capture
```

Set in docker-compose files or export before running:
```bash
export FLAG="centralctf{your_custom_flag}"
python app.py
```

## 🧪 Testing the Service

### 1. Basic Functionality
```bash
# Check if service is running
curl http://localhost:5000

# Register a user
curl -X POST http://localhost:5000/register \
  -d "username=test&password=test123"

# Login
curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "username=test&password=test123"

# Update profile
curl -b cookies.txt -X POST http://localhost:5000/update_profile \
  -d "bio=Hello&website=http://example.com"
```

### 2. Admin Bot Test
```bash
# Report a URL (requires authenticated session)
curl -b cookies.txt -X POST http://localhost:5000/report \
  -d "url=http://example.com"
```

## 🎓 Educational Value

### Learning Objectives
1. Understanding CSRF attacks
2. Session management and cookies
3. Same-origin policy
4. CSRF protection mechanisms
5. Security by design principles

### Skills Practiced
- Web vulnerability research
- Exploit development
- HTML/JavaScript
- HTTP protocol understanding
- Docker deployment

## 📚 Additional Files

### exploit_example.html
Reference exploit showing three different approaches:
1. Direct form submission
2. Auto-submit with JavaScript
3. Delayed submission

### .gitignore
Excludes:
- Python cache files
- Database files
- IDE configurations
- OS-specific files
- Docker artifacts

## 🔧 Maintenance

### Updating the Flag
Edit docker-compose file and rebuild:
```bash
docker-compose -f docker-compose.simple.yml down
# Edit FLAG in docker-compose.simple.yml
docker-compose -f docker-compose.simple.yml up --build -d
```

### Resetting the Database
```bash
docker-compose -f docker-compose.simple.yml down -v
docker-compose -f docker-compose.simple.yml up -d
```

### Viewing Logs
```bash
docker-compose -f docker-compose.simple.yml logs -f
```

## 🛡️ Security Considerations

**For Production Use (NOT recommended):**
- Add CSRF protection (Flask-WTF)
- Use HTTPS only
- Add rate limiting
- Implement proper session management
- Add input validation
- Use prepared statements (already done)
- Add password requirements
- Implement account lockout
- Add audit logging

**This is a deliberately vulnerable application for educational purposes only!**

## 📖 Related Documentation

- `README.md` - General overview and setup
- `QUICKSTART.md` - Quick start guide for students
- `SOLUTION.md` - Complete solution walkthrough (for instructors)
- `exploit_example.html` - Example exploit implementations

## 🎯 Success Criteria

Students successfully complete the challenge when they:
1. ✅ Identify the CSRF vulnerability
2. ✅ Understand the admin bot mechanism
3. ✅ Create a working exploit
4. ✅ Obtain the flag from admin's profile
5. ✅ Explain the attack and defense

---

**Version:** 1.0  
**Last Updated:** 2024  
**Target Audience:** CTF participants, security students, web developers