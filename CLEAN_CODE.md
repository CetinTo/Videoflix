# Clean Code Guidelines - Videoflix

This document describes the clean code principles applied in this project.

## ✅ Applied Clean Code Principles

### 1. Function Length

**Rule:** Functions are maximum 14 lines long

**Implementation:**
- All functions in `views.py` are ≤ 14 lines
- All functions in `tasks.py` are ≤ 14 lines
- Helper functions extracted to `utils.py`

**Example:**
```python
# ❌ Bad: 70+ lines
def login(request):
    # ... validation
    # ... authentication  
    # ... token generation
    # ... cookie setting
    # ... response creation
    
# ✅ Good: 14 lines
def post(self, request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email and password are required'})
    
    user = authenticate_user(email, password)
    if not user or not user.is_active:
        return Response({'error': 'Invalid credentials'})
    
    tokens = generate_jwt_tokens(user)
    response = self._create_login_response(user)
    set_auth_cookies(response, tokens['access'], tokens['refresh'])
    return response
```

### 2. Single Responsibility Principle

**Rule:** Each function does exactly ONE task

**Implementation:**
- `authenticate_user()` - only authentication
- `generate_jwt_tokens()` - only token generation
- `set_auth_cookies()` - only cookie setting
- `send_activation_email()` - only email sending

**Example:**
```python
# ❌ Bad: Multiple responsibilities
def login(request):
    user = authenticate(...)  # Authentication
    tokens = generate_tokens(user)  # Token generation
    response.set_cookie(...)  # Cookie setting
    return response  # Response creation

# ✅ Good: Single responsibilities
def authenticate_user(email, password):
    """Authenticate user - ONE task"""
    user = get_user_by_email(email)
    if not user:
        return None
    return authenticate(username=user.username, password=password)

def generate_jwt_tokens(user):
    """Generate tokens - ONE task"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }
```

### 3. Naming Conventions

**Rule:** All functions use snake_case convention

**Implementation:**
- ✅ `authenticate_user()`
- ✅ `generate_jwt_tokens()`
- ✅ `send_activation_email()`
- ✅ `convert_video_to_hls()`
- ✅ `get_video_duration_seconds()`

### 4. Descriptive Variable Names

**Rule:** Self-explanatory variable names throughout

**Implementation:**
```python
# ✅ Good names
access_token = tokens['access']
refresh_token = tokens['refresh']
duration_seconds = get_video_duration_seconds(path)
quality_settings = get_quality_settings(resolution)
hls_directory = create_hls_directory(path, resolution)

# ❌ Bad names
t = tokens['access']  # Not descriptive
d = get_duration(p)   # Too short
x = get_settings(y)   # Meaningless
```

### 5. No Unused Variables/Functions

**Rule:** All declared variables and functions are used

**Implementation:**
- Regular code reviews
- Linter checks for unused imports
- No dead code in codebase

### 6. No Commented Code

**Rule:** Commented code removed

**Implementation:**
- All old/commented code removed
- Only meaningful comments remain
- Docstrings for documentation

## 📁 File Organization

### Django-Specific Structure

**Rule:** Code in correct file locations

**Implementation:**

#### views.py
✅ **Only views that return HTTPResponse**
```python
class LoginView(APIView):
    def post(self, request):
        # ... 
        return Response(data, status=status.HTTP_200_OK)
```

#### utils.py / functions.py
✅ **Helper functions**
```python
def authenticate_user(email, password):
    """Helper function for authentication"""
    # ...
    
def generate_jwt_tokens(user):
    """Helper function for token generation"""
    # ...
```

#### tasks.py
✅ **Asynchronous background tasks**
```python
def process_uploaded_video(video_id):
    """Background task for video processing"""
    # ...
```

## 📦 Module Structure

```
users/
├── views.py          # Only HTTP response views
├── utils.py          # Helper functions (NEW)
├── models.py         # Database models
├── serializers.py    # DRF serializers
└── admin.py          # Admin configuration

videos/
├── views.py          # Only HTTP response views
├── utils.py          # Helper functions (NEW)
├── tasks.py          # RQ background tasks
├── models.py         # Database models
├── serializers.py    # DRF serializers
└── admin.py          # Admin configuration
```

## 🔍 Code Review Checklist

Before committing, ensure:

- [ ] All functions ≤ 14 lines
- [ ] Each function has ONE responsibility
- [ ] snake_case naming for all functions
- [ ] Descriptive variable names
- [ ] No unused variables/functions
- [ ] No commented code
- [ ] Views in `views.py` return HTTPResponse
- [ ] Helper functions in `utils.py`
- [ ] Background tasks in `tasks.py`
- [ ] Proper docstrings

## 📖 Further Reading

- **Django Email:** [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- **FFmpeg HLS:** [FFmpeg HLS Guide](https://ffmpeg.org/ffmpeg-formats.html#hls-2)
- **Clean Code:** Robert C. Martin - "Clean Code: A Handbook of Agile Software Craftsmanship"
