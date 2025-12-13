
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
import json
import requests
import traceback
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm, UserUpdateForm, PasswordChangeForm
from .models import UserProfile
from django.db import transaction
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from datetime import datetime



from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings




# ---------- Authentication Views ----------
def user_register(request):
    """
    Handle user registration with proper error handling and messaging
    """
    # Redirect authenticated users to home
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create user
                    user = form.save()
                    
                    # Handle profile creation safely
                    if hasattr(user, 'userprofile'):
                        # Profile exists, update it
                        profile = user.userprofile
                    else:
                        # Profile doesn't exist, create it
                        profile = UserProfile(user=user)
                    
                    # Update profile fields
                    if form.cleaned_data.get('phone'):
                        profile.phone = form.cleaned_data.get('phone')
                    if form.cleaned_data.get('age'):
                        profile.age = form.cleaned_data.get('age')
                    if form.cleaned_data.get('health_condition'):
                        profile.health_condition = form.cleaned_data.get('health_condition')
                    if form.cleaned_data.get('medications'):
                        profile.medications = form.cleaned_data.get('medications')
                    
                    profile.save()
                
                # SUCCESS: Show message and redirect to login page (DO NOT auto-login)
                messages.success(request, 'Account created successfully! Please login to continue.')
                return redirect('login')
                
            except Exception as e:
                # More detailed error logging
                error_message = f"Registration error: {str(e)}"
                print(error_message)
                messages.error(request, 'Registration failed. Please try again.')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = UserRegisterForm()
    
    return render(request, 'register.html', {'form': form})

def user_login(request):
    """
    Handle user login with proper authentication
    """
    print(f"DEBUG: Login view called - Method: {request.method}")
    print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
    
    # Redirect authenticated users to home
    if request.user.is_authenticated:
        print("DEBUG: User already authenticated, redirecting to home")
        return redirect('home')
    
    if request.method == 'POST':
        # Use direct form processing instead of form class for better debugging
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        print(f"DEBUG: Login attempt - Username: {username}")
        
        # Basic validation
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html', {'username_value': username})
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        print(f"DEBUG: Authentication result: {user}")
        
        if user is not None:
            if user.is_active:
                login(request, user)
                print("DEBUG: Login successful, redirecting to home")
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page if specified, otherwise to home
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('home')
            else:
                messages.error(request, 'Your account is inactive.')
        else:
            print("DEBUG: Login failed - invalid credentials")
            messages.error(request, 'Invalid username or password. Please try again.')
    
    # If GET request or failed login, show login form
    return render(request, 'login.html')

def user_logout(request):
    """
    Handle user logout
    """
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile(request):
    """
    User profile page with update functionality
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'profile.html', {
        'user': request.user,
        'profile': user_profile,
        'form': form
    })

# ---------- Page Views ----------
def home(request):
    """
    Home page view
    """
    return render(request, 'index.html')

@login_required
def dashboard(request):
    """
    User dashboard with health insights
    """
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    
    # Basic health stats (you can expand this with real data)
    health_stats = {
        'games_played': 0,
        'chat_messages': 0,
        'health_score': 100,  # Basic placeholder
    }
    
    return render(request, 'dashboard.html', {
        'user_profile': user_profile,
        'health_stats': health_stats
    })

@login_required
def health_game(request):
    """
    Health education game page
    """
    return render(request, 'health_game.html')

@login_required
def sort_the_food(request):
    """
    Food sorting educational game
    """
    return render(request, 'sort_the_food.html')

@login_required
def myth_vs_fact(request):
    """
    Myth vs Fact educational game
    """
    return render(request, 'myth_vs_fact.html')

@login_required
def meditation(request):
    """
    Meditation and wellness page
    """
    return render(request, 'meditation.html')

@login_required
def Safety_Simon(request):
    """
    Safety education game - Fixed function name (lowercase)
    """
    return render(request, 'Safety_Simon.html')

def entertainment(request):
    """
    Entertainment and comics page (accessible without login)
    """
    images = [
        'comics/comic1.jpg',
        'comics/comic2.jpg',
        'comics/comic3.jpg',
        'comics/comic4.jpg',
        'comics/comic5.jpg',
        'comics/comic6.jpg',
    ]
    return render(request, 'entertainment.html', {'images': images})



# ---------- Enhanced Chatbot System ----------

# Comprehensive health knowledge base
HEALTH_KNOWLEDGE_BASE = {
    # Vaccines
    'covid vaccine': {
        'response': """💉 **COVID-19 Vaccine Information** 🦠

*Available Vaccines:*
• mRNA vaccines (Pfizer, Moderna)
• Protein subunit vaccines (Novavax)
• Vector vaccines (Johnson & Johnson)

*Common Side Effects:*
• Pain at injection site
• Fatigue, headache
• Muscle pain, fever
• Chills, nausea

*Effectiveness:* High protection against severe disease (90%+)

*Booster Recommendation:* Stay updated as per health authority guidelines

*Precautions:* Consult doctor if immunocompromised or have history of severe allergies""",
        'category': 'vaccine'
    },
    
    'flu vaccine': {
        'response': """💉 **Influenza (Flu) Vaccine** 🤧

*Types Available:*
• Standard quadrivalent
• High-dose (for seniors)
• Egg-free options
• Nasal spray (LAIV)

*When to Get:* Annually, before flu season (October-November)

*Who Should Get:* Everyone 6 months and older

*Effectiveness:* 40-60% effective in preventing flu

*Special Groups:* Essential for pregnant women, seniors, children""",
        'category': 'vaccine'
    },
    
    'mmr vaccine': {
        'response': """💉 **MMR Vaccine (Measles, Mumps, Rubella)**

*Schedule:* 2 doses (12-15 months & 4-6 years)

*Importance:* Prevents serious childhood diseases

*Effectiveness:* 97% effective against measles

*Side Effects:* Mild fever, rash (7-12 days after)

*Contraindications:* Pregnancy, severe immunodeficiency""",
        'category': 'vaccine'
    },
    
    'hpv vaccine': {
        'response': """💉 **HPV Vaccine (Human Papillomavirus)**

*Recommended Age:* 11-12 years (can start at 9)

*Doses:* 2 doses if started before 15, 3 doses after

*Protection:* Prevents cervical cancer, genital warts

*Duration:* Long-lasting protection

*Safety:* Extensive safety record""",
        'category': 'vaccine'
    },
    
    # Diseases
    'diabetes': {
        'response': """🩸 **Diabetes Information**

*Types:*
• Type 1: Autoimmune, insulin-dependent
• Type 2: Insulin resistance, lifestyle-related
• Gestational: During pregnancy

*Symptoms:*
• Frequent urination
• Excessive thirst
• Unexplained weight loss
• Fatigue, blurred vision

*Management:*
• Blood sugar monitoring
• Healthy diet, regular exercise
• Medication/insulin as prescribed
• Regular check-ups""",
        'category': 'disease'
    },
    
    'hypertension': {
        'response': """🫀 **Hypertension (High Blood Pressure)**

*Classification:*
• Normal: <120/80 mmHg
• Elevated: 120-129/<80
• Stage 1: 130-139/80-89
• Stage 2: ≥140/≥90

*Risk Factors:*
• Family history, age
• Obesity, sedentary lifestyle
• High salt intake, alcohol
• Stress, smoking

*Management:*
• DASH diet, weight management
• Regular exercise, stress reduction
• Medication adherence
• Regular monitoring""",
        'category': 'disease'
    },
    
    'asthma': {
        'response': """🌬️ **Asthma Management**

*Symptoms:*
• Wheezing, coughing
• Shortness of breath
• Chest tightness
• Nighttime symptoms

*Triggers:*
• Allergens (pollen, dust)
• Respiratory infections
• Exercise, cold air
• Stress, smoke

*Treatment:*
• Quick-relief inhalers
• Long-term control medications
• Avoid triggers
• Action plan with doctor""",
        'category': 'disease'
    },
    
    'malaria': {
        'response': """🦟 **Malaria Prevention & Treatment**

*Transmission:* Mosquito bites (Anopheles mosquito)

*Symptoms:*
• High fever, chills
• Headache, muscle pain
• Fatigue, nausea
• Sweating, abdominal pain

*Prevention:*
• Mosquito nets, repellents
• Antimalarial medication
• Protective clothing
• Eliminate breeding sites

*Treatment:* Prompt medical care, antimalarial drugs""",
        'category': 'disease'
    },
    
    # Diets
    'keto diet': {
        'response': """🥑 **Keto Diet Guide**

*Macronutrient Ratio:*
• 70-80% Fat
• 20-25% Protein
• 5-10% Carbohydrates

*Foods to Eat:*
• Meat, fatty fish, eggs
• Butter, oils, avocados
• Low-carb vegetables
• Nuts, seeds, cheese

*Foods to Avoid:*
• Grains, sugar
• Fruits, starchy vegetables
• Legumes, most processed foods

*Considerations:*
• Monitor ketone levels
• Stay hydrated, electrolyte balance
• Consult doctor if diabetic""",
        'category': 'diet'
    },
    
    'mediterranean diet': {
        'response': """🐟 **Mediterranean Diet**

*Key Components:*
• Fruits and vegetables
• Whole grains, legumes
• Olive oil, nuts, seeds
• Fish and seafood
• Moderate dairy, wine

*Benefits:*
• Heart health improvement
• Weight management
• Reduced inflammation
• Better brain function

*Lifestyle Elements:*
• Physical activity
• Social meals
• Stress management""",
        'category': 'diet'
    },
    
    'dash diet': {
        'response': """🫀 **DASH Diet (Hypertension)**

*Daily Servings:*
• Grains: 6-8
• Vegetables: 4-5
• Fruits: 4-5
• Dairy: 2-3 (low-fat)
• Protein: 6 or less

*Sodium Limit:* 1500-2300 mg daily

*Emphasize:*
• Potassium-rich foods
• Magnesium, calcium
• Fiber, lean proteins

*Avoid:*
• High-sodium processed foods
• Sugary beverages
• Saturated fats""",
        'category': 'diet'
    },
    
    # Prevention
    'heart disease prevention': {
        'response': """❤️ **Heart Disease Prevention**

*Lifestyle Changes:*
• No smoking, limit alcohol
• Regular exercise (150 mins/week)
• Healthy weight maintenance
• Stress management

*Dietary Recommendations:*
• Limit saturated/trans fats
• Increase fiber intake
• Omega-3 fatty acids
• Limit sodium, added sugars

*Medical Management:*
• Control blood pressure
• Manage cholesterol
• Control diabetes
• Regular check-ups""",
        'category': 'prevention'
    },
    
    'cancer prevention': {
        'response': """🦀 **Cancer Prevention Strategies**

*Lifestyle Factors:*
• No tobacco in any form
• Limit alcohol consumption
• Maintain healthy weight
• Regular physical activity

*Dietary Recommendations:*
• Fruits and vegetables
• Whole grains, fiber
• Limit processed meats
• Balanced, varied diet

*Early Detection:*
• Regular screenings
• Know family history
• Self-examinations
• Prompt medical attention""",
        'category': 'prevention'
    }
}

# Fallback responses for general categories
CATEGORY_FALLBACKS = {
    'vaccine': """💉 **Vaccine Information**

I can provide details about:
• COVID-19 vaccines
• Influenza (flu) vaccine
• MMR (measles, mumps, rubella)
• HPV vaccine
• Childhood immunization schedule
• Travel vaccines

What specific vaccine would you like to know about?""",
    
    'disease': """🩺 **Disease Information**

I can explain about:
• Diabetes and management
• Hypertension (high BP)
• Asthma and respiratory issues
• Heart conditions
• Infectious diseases
• Chronic illnesses

Which disease are you interested in?""",
    
    'diet': """🥗 **Nutrition & Diets**

I can guide you on:
• Keto diet
• Mediterranean diet
• DASH diet (for hypertension)
• Diabetic diet plans
• Weight management diets
• Heart-healthy eating

What type of diet information do you need?""",
    
    'prevention': """🛡️ **Disease Prevention**

I can help with prevention of:
• Heart disease
• Diabetes
• Cancer
• Infectious diseases
• Chronic conditions
• Seasonal illnesses

What would you like to prevent?"""
}




# ---------- API Views ----------
@csrf_exempt
def chatbot_api(request):
    """
    AI Chatbot API endpoint - communicates with Rasa
    """
    if request.method == "POST":
        try:
            # Parse request data
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            language = data.get("language", "en")
            user_id = data.get("user_id", "anonymous")

            # Validate input
            if not user_message:
                return JsonResponse({"error": "No message provided."}, status=400)

            # Rasa server URLs to try
            rasa_urls = [
                "http://127.0.0.1:5005/webhooks/rest/webhook",
                "http://localhost:5005/webhooks/rest/webhook", 
            ]
            
            response = None
            
            # Try each Rasa URL
            for rasa_url in rasa_urls:
                try:
                    response = requests.post(
                        rasa_url,
                        json={
                            "sender": f"user_{user_id}",
                            "message": user_message,
                            "metadata": {
                                "language": language,
                                "user_id": user_id
                            }
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException:
                    continue

            # Handle Rasa connection failure
            if not response or response.status_code != 200:
                fallback_replies = get_intelligent_fallback_response(user_message, language)
                return JsonResponse({
                    "replies": fallback_replies,
                    "source": "fallback",
                    "status": "rasa_unavailable"
                }, status=200)

            # Parse Rasa response
            try:
                bot_responses = response.json()
                replies = [msg.get("text", "") for msg in bot_responses if "text" in msg]
                
                if not replies:
                    replies = get_intelligent_fallback_response(user_message, language)
                    source = "fallback"
                else:
                    source = "rasa"
                    
            except json.JSONDecodeError:
                replies = get_intelligent_fallback_response(user_message, language)
                source = "fallback"

            return JsonResponse({
                "replies": replies,
                "source": source,
                "status": "success"
            }, status=200)

        except Exception as e:
            print(f"Chatbot API error: {str(e)}")
            return JsonResponse({
                "replies": get_intelligent_fallback_response("", "en"),
                "source": "error_fallback",
                "status": "error"
            }, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

def find_health_response(message):
    """Find response in comprehensive health knowledge base"""
    message_lower = message.lower()
    
    # Check for exact matches first
    for key, info in HEALTH_KNOWLEDGE_BASE.items():
        if key in message_lower:
            return info['response']
    
    # Check for category matches
    if any(word in message_lower for word in ['vaccine', 'vaccination', 'immunization', 'shot']):
        return CATEGORY_FALLBACKS['vaccine']
    
    elif any(word in message_lower for word in ['disease', 'illness', 'sickness', 'condition', 'disorder']):
        return CATEGORY_FALLBACKS['disease']
    
    elif any(word in message_lower for word in ['diet', 'nutrition', 'food', 'eat', 'meal', 'dietary']):
        return CATEGORY_FALLBACKS['diet']
    
    elif any(word in message_lower for word in ['prevent', 'prevention', 'avoid', 'protection']):
        return CATEGORY_FALLBACKS['prevention']
    
    return None

def try_rasa_response(message, user_id):
    """Try to get response from Rasa with fallback"""
    try:
        rasa_urls = [
            "http://127.0.0.1:5005/webhooks/rest/webhook",
            "http://localhost:5005/webhooks/rest/webhook", 
        ]
        
        for rasa_url in rasa_urls:
            try:
                response = requests.post(
                    rasa_url,
                    json={
                        "sender": f"user_{user_id}",
                        "message": message
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    bot_responses = response.json()
                    if bot_responses:
                        return bot_responses[0].get("text", "")
            except:
                continue
                
    except Exception as e:
        print(f"Rasa connection error: {str(e)}")
    
    return None


def get_intelligent_health_response(message):
    """Generate intelligent health response based on message content"""
    message_lower = message.lower()
    
    # Symptom-related queries
    if any(word in message_lower for word in ['fever', 'temperature']):
        return """🌡️ **Fever Management**

*Self-Care:*
• Rest and stay hydrated
• Monitor temperature regularly
• Use cool compresses
• Over-the-counter fever reducers if needed

*When to See Doctor:*
• Fever above 102°F (39°C)
• Lasts more than 3 days
• Accompanied by rash, stiff neck, or confusion
• In infants under 3 months

💡 Always consult healthcare provider for persistent symptoms"""
    
    elif any(word in message_lower for word in ['headache', 'migraine']):
        return """🤕 **Headache Relief**

*Immediate Relief:*
• Rest in quiet, dark room
• Stay hydrated
• Cold or warm compress
• Gentle massage

*Prevention:*
• Regular sleep schedule
• Stress management
• Identify and avoid triggers
• Regular meals

🚨 Seek emergency care for sudden severe headache or with neurological symptoms"""
    
    elif any(word in message_lower for word in ['cough', 'coughing']):
        return """🤧 **Cough Management**

*Home Remedies:*
• Honey with warm water/tea
• Steam inhalation
• Stay well hydrated
• Use humidifier

*Medical Attention Needed For:*
• Cough lasting >3 weeks
• Difficulty breathing
• Chest pain
• Coughing up blood
• High fever with cough

💡 Avoid irritants like smoke and strong fumes"""
    
    # General health queries
    elif any(word in message_lower for word in ['exercise', 'workout', 'fitness']):
        return """💪 **Exercise Guidelines**

*General Recommendations:*
• 150 mins moderate or 75 mins vigorous exercise weekly
• Strength training 2x/week
• Include flexibility exercises
• Stay active throughout day

*Benefits:*
• Weight management
• Heart health improvement
• Better mental health
• Reduced disease risk

💡 Start slowly and consult doctor if new to exercise"""
    
    elif any(word in message_lower for word in ['sleep', 'insomnia']):
        return """😴 **Sleep Health**

*Recommended Duration:*
• Adults: 7-9 hours
• Teenagers: 8-10 hours
• Children: 9-12 hours
• Preschoolers: 10-13 hours

*Sleep Hygiene:*
• Consistent sleep schedule
• Dark, quiet, cool bedroom
• No screens before bed
• Relaxing bedtime routine

💡 Consult doctor for persistent sleep issues"""
    
    # Default comprehensive response
    return """👋 **Health Assistant**

I can help you with comprehensive health information including:

💉 *Vaccines:* COVID-19, flu, MMR, HPV, travel vaccines
🩺 *Diseases:* Diabetes, hypertension, asthma, heart conditions
🥗 *Diets:* Keto, Mediterranean, DASH, weight management
🛡️ *Prevention:* Heart disease, cancer, diabetes prevention
🤒 *Symptoms:* Fever, headache, cough, pain management
💪 *Lifestyle:* Exercise, nutrition, sleep, stress management

What specific health topic would you like to know about?"""



def get_intelligent_fallback_response(message, language):
    """
    Provide intelligent fallback responses when Rasa is unavailable
    """
    message_lower = message.lower()
    
    healthcare_knowledge = {
        "en": {
            "greeting": [
                "👋 Hello! I'm your AI Health Assistant specializing in vaccines, symptoms, and prevention. How can I help you today?"
            ],
            "default": [
                "💊 I specialize in healthcare information including vaccines, symptoms, and prevention tips. What would you like to know?"
            ]
        },
        "hi": {
            "greeting": [
                "👋 नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं। वैक्सीन, लक्षण और रोकथाम में विशेषज्ञता। आज मैं आपकी कैसे मदद कर सकता हूं?"
            ],
            "default": [
                "💊 मैं स्वास्थ्य जानकारी में माहिर हूं including वैक्सीन, लक्षण और रोकथाम टिप्स। आप क्या जानना चाहेंगे?"
            ]
        },
        "or": {
            "greeting": [
                "👋 ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କର AI ସ୍ୱାସ୍ଥ୍ୟ ସହାୟକ। ଭାକ୍ସିନ୍, ଲକ୍ଷଣ ଏବଂ ପ୍ରତିଷେଧରେ ବିଶେଷଜ୍ଞତା। ଆଜି ମୁଁ ଆପଣଙ୍କୁ କିପରି ସାହାଯ୍ୟ କରିପାରିବି?"
            ],
            "default": [
                "💊 ମୁଁ ସ୍ୱାସ୍ଥ୍ୟ ତଥ୍ୟରେ ବିଶେଷଜ୍ଞ including ଭାକ୍ସିନ୍, ଲକ୍ଷଣ ଏବଂ ପ୍ରତିଷେଧ ଟିପ୍ସ। ଆପଣ କ'ଣ ଜାନିବାକୁ ଚାହାଁନ୍ତି?"
            ]
        }
    }
    
    lang_responses = healthcare_knowledge.get(language, healthcare_knowledge["en"])
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'namaste', 'ନମସ୍କାର', 'नमस्ते']):
        return lang_responses.get("greeting", lang_responses["default"])
    else:
        return lang_responses["default"]

@csrf_exempt
def health_check(request):
    """
    Health check endpoint for monitoring
    """
    if request.method == "GET":
        try:
            response = requests.get("http://127.0.0.1:5005/", timeout=5)
            rasa_status = "connected" if response.status_code == 200 else "disconnected"
            return JsonResponse({"status": "healthy", "rasa_server": rasa_status, "django": "running"})
        except:
            return JsonResponse({"status": "healthy", "rasa_server": "disconnected", "django": "running"})
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def register_api(request):
    """
    API endpoint for user registration
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in data or not data[field].strip():
                    return JsonResponse({"error": f"Missing required field: {field}"}, status=400)
            
            if User.objects.filter(username=data['username']).exists():
                return JsonResponse({"error": "Username already exists"}, status=400)
            
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            UserProfile.objects.create(user=user)
            
            return JsonResponse({
                "message": "Registration successful", 
                "user": {
                    "username": data['username'], 
                    "email": data['email']
                }
            }, status=201)
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def test_chatbot_connection(request):
    """
    Test endpoint to verify chatbot connectivity
    """
    if request.method == "POST":
        try:
            response = requests.post(
                "http://127.0.0.1:5005/webhooks/rest/webhook",
                json={"sender": "test_user", "message": "hello"},
                timeout=10
            )
            
            if response.status_code == 200:
                bot_responses = response.json()
                return JsonResponse({
                    "status": "connected",
                    "message": "Rasa chatbot is responding correctly",
                    "response": bot_responses
                }, status=200)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Rasa returned status code: {response.status_code}"
                }, status=200)
                
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                "status": "disconnected",
                "message": "Cannot connect to Rasa server on port 5005"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=200)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

# ---------- Utility Views ----------
def handler404(request, exception):
    """
    Custom 404 error handler
    """
    return render(request, '404.html', status=404)

def handler500(request):
    """
    Custom 500 error handler
    """
    return render(request, '500.html', status=500)

# ---------- Profile Management Views ----------
@login_required
def edit_profile(request):
    """
    Edit user profile information
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def change_password(request):
    """
    Change user password
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

@login_required
@require_POST
def delete_account(request):
    """
    Delete user account
    """
    user = request.user
    logout(request)  # Logout first to clear session
    user.delete()  # This will also delete the UserProfile due to CASCADE
    messages.success(request, 'Your account has been deleted successfully.')
    return redirect('home')

@login_required
def profile_settings(request):
    """
    Profile settings page with all management options
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profile_settings.html', {
        'user_profile': user_profile
    })






# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

@csrf_exempt
def whatsapp_webhook(request):
    """
    Handle incoming WhatsApp messages via Twilio
    """
    if request.method == 'POST':
        try:
            # Get incoming message details
            incoming_msg = request.POST.get('Body', '').strip()
            from_number = request.POST.get('From', '')
            
            print(f"WhatsApp message from {from_number}: {incoming_msg}")
            
            # Create response
            response = MessagingResponse()
            
            # Process the message
            if incoming_msg:
                bot_response = process_whatsapp_message(incoming_msg, from_number)
                response.message(bot_response)
            else:
                welcome_msg = """👋 Hello! I'm your Health Assistant. I can help you with:

💉 Vaccine information
🤒 Symptom checking
🥗 Diet & nutrition
🛡 Disease prevention
🏥 Health facilities

What would you like to know?

💡 Try: vaccines, symptoms, diet, or prevention"""
                response.message(welcome_msg)
            
            return HttpResponse(str(response))
            
        except Exception as e:
            print(f"WhatsApp webhook error: {str(e)}")
            response = MessagingResponse()
            response.message("Sorry, I'm having trouble processing your request. Please try again.")
            return HttpResponse(str(response))
    
    return HttpResponse("GET request received")


def process_whatsapp_message(message, user_id):
    """
    Process WhatsApp messages with clean, integrated responses
    """
    try:
        # First, try to get response from Rasa
        response = requests.post(
            "http://127.0.0.1:8000/api/chatbot/",
            json={
                "message": message,
                "user_id": f"whatsapp_{user_id}",
                "language": "en"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            replies = data.get('replies', [])
            
            # If Rasa has a good response, use it and add suggestions
            if replies and not is_generic_response(replies[0]):
                main_response = "\n".join(replies)
                suggestions = get_quick_suggestions(message)  # Add suggestions here
                return main_response + suggestions
            else:
                # If Rasa returns generic response, use our custom response
                return get_custom_health_response(message)
        else:
            # If Rasa fails, use our custom response
            return get_custom_health_response(message)
            
    except Exception as e:
        print(f"Chatbot processing error: {str(e)}")
        return get_custom_health_response(message)


def is_generic_response(response):
    """Check if the response is a generic fallback"""
    generic_phrases = [
        "I specialize in healthcare information",
        "What would you like to know",
        "I can help with healthcare information",
        "vaccines, symptoms, and prevention tips"
    ]
    return any(phrase in response for phrase in generic_phrases)



def get_custom_health_response(message):
    """Provide custom health responses for WhatsApp"""
    message_lower = message.lower()
    
    # Diet and Nutrition - CHECK FIRST with exclusions
    diet_keywords = ['diet', 'food', 'nutrition', 'eat', 'meal', 'healthy eating']
    symptom_keywords = ['pain', 'hurt', 'ache', 'symptom', 'fever', 'headache', 'cough']
    
    has_diet_keyword = any(word in message_lower for word in diet_keywords)
    has_symptom_keyword = any(word in message_lower for word in symptom_keywords)
    
    if has_diet_keyword and not has_symptom_keyword:
        if any(word in message_lower for word in ['general', 'basic', 'normal', 'regular', 'standard', 'healthy eating']):
            return """🥗 *General Healthy Eating Guide*

*Balanced Diet Principles:*
• Fill half your plate with fruits & vegetables
• Choose whole grains (brown rice, whole wheat)
• Include lean proteins (chicken, fish, lentils)
• Healthy fats (avocado, nuts, olive oil)
• Limit processed foods and sugar
• Stay hydrated with water

*Daily Goals:*
• 5+ servings of fruits/vegetables
• Variety of colors for different nutrients
• Moderate portion sizes
• Regular meal timing

💡 *Quick options:* Type 'meal plans', 'weight management', or 'diet for conditions'"""
        
        elif any(word in message_lower for word in ['weight', 'loss', 'slimming', 'obesity', 'weight management']):
            return """⚖️ *Weight Management Diet*

*Healthy Weight Loss Strategies:*
• Calorie control with nutrient-dense foods
• Regular physical activity (150 mins/week)
• Portion control and mindful eating
• High protein intake for satiety
• Limit sugar and processed foods

*Key Principles:*
• 1-2 lbs weight loss per week is safe
• Combine cardio and strength training
• Stay hydrated (8-10 glasses water/day)
• Get adequate sleep (7-9 hours)

💡 *Sustainable changes work better than quick fixes*"""
        
        elif any(word in message_lower for word in ['gluten', 'celiac']):
            return """🥗 *Gluten-Free Diet Information* 🌾

*For:* Celiac disease, gluten sensitivity, wheat allergy

*Naturally Gluten-Free Foods:*
• Fruits and vegetables
• Meat, poultry, fish (unbreaded)
• Rice, quinoa, corn
• Potatoes, sweet potatoes
• Legumes, nuts, seeds

*Foods to Avoid:*
• Wheat, barley, rye
• Most breads, pasta, cereals
• Beer and malt beverages
• Many processed foods

*Important:* Read labels carefully, watch for cross-contamination

⚠️ *Consult dietitian for complete gluten-free guidance*"""
        
        elif any(word in message_lower for word in ['meal plan', 'meal plans', 'daily meal', 'weekly meal', 'diet plan']):
            return """📅 *Sample Healthy Meal Plan*

*Breakfast Options:*
• Oatmeal with berries and nuts
• Whole grain toast with avocado and eggs
• Greek yogurt with fruit and honey
• Smoothie with spinach, banana, and protein

*Lunch Options:*
• Grilled chicken salad with mixed greens
• Quinoa bowl with roasted vegetables
• Whole grain wrap with hummus and veggies
• Lentil soup with whole grain bread

*Dinner Options:*
• Baked salmon with sweet potato and broccoli
• Stir-fried tofu with brown rice and vegetables
• Lean beef with quinoa and asparagus
• Chicken and vegetable skewers

*Healthy Snacks:*
• Apple slices with peanut butter
• Carrot sticks with hummus
• Handful of nuts and seeds
• Greek yogurt with berries"""
        
        elif any(word in message_lower for word in ['condition', 'conditions', 'disease', 'medical']):
            return """🏥 *Diet for Specific Health Conditions*

I can provide dietary guidance for:

*Heart Conditions:*
• Low sodium, low saturated fat
• High fiber, omega-3 fatty acids
• DASH diet principles

*Diabetes:*
• Carbohydrate counting
• Glycemic index awareness
• Regular meal timing

*Digestive Issues:*
• High fiber for constipation
• Low FODMAP for IBS
• Gluten-free for celiac

*Kidney Disease:*
• Protein and potassium control
• Phosphorus management
• Fluid balance

💡 *Please specify which condition you're interested in for detailed guidance.*"""
        
        else:
            return """🥗 *Diet & Nutrition Guidance*

I can help you with:
• *General healthy eating* (type 'general healthy eating')
• *Weight management diets* (type 'weight management')
• *Meal planning* (type 'meal plans')
• *Condition-specific diets* (type 'diet for conditions')
• *Gluten-free eating* (type 'gluten free')

What specific dietary information do you need?"""
    
    # Vaccine Information
    elif any(word in message_lower for word in ['vaccine', 'vaccination', 'covid']):
        if any(word in message_lower for word in ['covid', 'corona']):
            return """💉 *COVID-19 Vaccine Information* 🦠

*Available Vaccines:*
• mRNA vaccines (Pfizer, Moderna)
• Protein subunit vaccines (Novavax)
• Vector vaccines (Johnson & Johnson)

*Common Side Effects:*
• Pain at injection site
• Fatigue, headache
• Muscle pain, fever
• Chills, nausea

*Effectiveness:* High protection against severe disease (90%+)

*Booster Recommendation:* Stay updated as per health authority guidelines

*Precautions:* Consult doctor if immunocompromised or have history of severe allergies"""
        
        elif any(word in message_lower for word in ['flu', 'influenza']):
            return """💉 *Influenza (Flu) Vaccine* 🤧

*Types Available:*
• Standard quadrivalent
• High-dose (for seniors)
• Egg-free options
• Nasal spray (LAIV)

*When to Get:* Annually, before flu season (October-November)

*Who Should Get:* Everyone 6 months and older

*Effectiveness:* 40-60% effective in preventing flu

*Special Groups:* Essential for pregnant women, seniors, children"""
        
        else:
            return """💉 *Vaccine Information*

*COVID-19 Vaccines:*
• mRNA vaccines (Pfizer, Moderna)
• Protein subunit (Novavax)
• Vector vaccines (Johnson & Johnson)
• High protection against severe disease

*Other Vaccines:*
• Flu shots (annual)
• Childhood immunization schedule
• Travel vaccines
• HPV, Hepatitis, etc.

💡 *Quick options:* Type 'covid vaccine', 'child vaccines', or 'travel vaccines'"""
    
    # Prevention - CHECK BEFORE SYMPTOMS
    elif any(word in message_lower for word in ['prevention', 'prevent', 'avoid']):
        if 'fever' in message_lower:
            return """🛡️ *Fever Prevention Strategies*

*General Prevention:*
• Practice good hand hygiene regularly
• Avoid close contact with sick individuals
• Maintain a strong immune system through balanced nutrition
• Stay hydrated throughout the day
• Get adequate rest and sleep

*Infection Prevention:*
• Keep up with recommended vaccinations
• Practice food safety and proper cooking
• Avoid sharing personal items when sick
• Clean and disinfect frequently touched surfaces

*Immune Support:*
• Eat a variety of fruits and vegetables
• Include immune-supporting nutrients (Vitamin C, Zinc)
• Engage in regular moderate exercise
• Maintain healthy gut microbiome

💡 *While fever itself isn't always preventable, these strategies reduce your risk of infections that commonly cause fever.*"""
        
        elif any(word in message_lower for word in ['heart', 'cardio']):
            return """❤️ *Heart Disease Prevention*

*Lifestyle Changes:*
• No smoking, limit alcohol
• Regular exercise (150 mins/week)
• Healthy weight maintenance
• Stress management

*Dietary Recommendations:*
• Limit saturated/trans fats
• Increase fiber intake
• Omega-3 fatty acids
• Limit sodium, added sugars

*Medical Management:*
• Control blood pressure
• Manage cholesterol
• Control diabetes
• Regular check-ups"""
        
        elif any(word in message_lower for word in ['cancer']):
            return """🦀 *Cancer Prevention Strategies*

*Lifestyle Factors:*
• No tobacco in any form
• Limit alcohol consumption
• Maintain healthy weight
• Regular physical activity

*Dietary Recommendations:*
• Fruits and vegetables
• Whole grains, fiber
• Limit processed meats
• Balanced, varied diet

*Early Detection:*
• Regular screenings
• Know family history
• Self-examinations
• Prompt medical attention"""
        
        else:
            return """🛡️ *Disease Prevention*

*General Prevention:*
• Wash hands frequently
• Balanced nutrition
• Regular exercise
• Adequate sleep (7-9 hours)
• Stress management
• Regular health check-ups

*Specific Prevention:*
• Vaccinations for preventable diseases
• Mosquito control for dengue/malaria
• Food safety practices
• Personal hygiene

💡 *Quick options:* Type 'disease prevention', 'vaccine prevention', or 'healthy lifestyle'"""
    
    # Symptom Checking - ONLY if no diet keywords
    elif any(word in message_lower for word in ['symptom', 'pain', 'fever', 'headache', 'cough', 'hurt', 'ache']) and not has_diet_keyword:
        # Check if it's about fever prevention specifically
        if 'fever' in message_lower and any(word in message_lower for word in ['prevent', 'avoid', 'stop', 'prevention']):
            return """🛡️ *Fever Prevention Strategies*

*General Prevention:*
• Practice good hand hygiene regularly
• Avoid close contact with sick individuals
• Maintain a strong immune system through balanced nutrition
• Stay hydrated throughout the day
• Get adequate rest and sleep

*Infection Prevention:*
• Keep up with recommended vaccinations
• Practice food safety and proper cooking
• Avoid sharing personal items when sick
• Clean and disinfect frequently touched surfaces

*Immune Support:*
• Eat a variety of fruits and vegetables
• Include immune-supporting nutrients (Vitamin C, Zinc)
• Engage in regular moderate exercise
• Maintain healthy gut microbiome

💡 *While fever itself isn't always preventable, these strategies reduce your risk of infections that commonly cause fever.*"""
        
        elif any(word in message_lower for word in ['fever', 'temperature']):
            return """🌡️ *Fever Information*

*Self-Care:*
• Rest and stay hydrated
• Monitor temperature regularly
• Use cool compresses
• Over-the-counter fever reducers if needed

*When to See Doctor:*
• Fever above 102°F (39°C)
• Lasts more than 3 days
• Accompanied by rash, stiff neck, or confusion
• In infants under 3 months

💡 Always consult healthcare provider for persistent symptoms"""
        
        elif any(word in message_lower for word in ['headache', 'migraine']):
            return """🤕 *Headache Relief*

*Immediate Relief:*
• Rest in quiet, dark room
• Stay hydrated
• Cold or warm compress
• Gentle massage

*Prevention:*
• Regular sleep schedule
• Stress management
• Identify and avoid triggers
• Regular meals

🚨 Seek emergency care for sudden severe headache or with neurological symptoms"""
        
        elif any(word in message_lower for word in ['cough', 'coughing']):
            return """🤧 *Cough Management*

*Home Remedies:*
• Honey with warm water/tea
• Steam inhalation
• Stay well hydrated
• Use humidifier

*Medical Attention Needed For:*
• Cough lasting >3 weeks
• Difficulty breathing
• Chest pain
• Coughing up blood
• High fever with cough

💡 Avoid irritants like smoke and strong fumes"""
        
        elif any(word in message_lower for word in ['pain', 'hurt', 'ache']):
            return """😣 *Pain Management*

*General Care:*
• Rest the affected area
• Use heat or cold therapy
• Over-the-counter pain relief if appropriate
• Gentle stretching if suitable

*When to Seek Medical Care:*
• Severe or worsening pain
• Pain after injury or accident
• Pain with fever or other symptoms
• Persistent pain that doesn't improve

🚨 *Emergency:* Chest pain, severe abdominal pain, or pain with difficulty breathing"""
        
        else:
            return """🤒 *Symptom Information*

*Common Symptoms & General Advice:*
• Fever: Rest, hydrate, monitor temperature
• Cough: Honey, steam inhalation, avoid irritants
• Headache: Rest, hydration, avoid triggers
• Always consult doctor for persistent symptoms

🚨 *Seek immediate medical help for:*
• Difficulty breathing
• Chest pain
• Severe headache
• High fever (104°F/40°C+)

💡 *Quick options:* Type 'common symptoms', 'emergency signs', or 'find doctor'"""
    
    # Emergency situations
    elif any(word in message_lower for word in ['emergency', 'urgent', '911', 'help now']):
        return """🚨 *MEDICAL EMERGENCY ALERT* 🚨

If you are experiencing a medical emergency:

• Call emergency services immediately (911/112/your local emergency number)
• Go to the nearest hospital emergency department
• Do not delay seeking medical attention

Common emergency signs:
• Chest pain or pressure
• Difficulty breathing
• Severe bleeding
• Sudden weakness or confusion
• Seizures

Your health and safety are the top priority! 🏥"""
    
    # Exercise and Fitness
    elif any(word in message_lower for word in ['exercise', 'workout', 'fitness', 'gym']):
        return """💪 *Exercise Guidelines*

*General Recommendations:*
• 150 mins moderate or 75 mins vigorous exercise weekly
• Strength training 2x/week
• Include flexibility exercises
• Stay active throughout day

*Benefits:*
• Weight management
• Heart health improvement
• Better mental health
• Reduced disease risk

💡 Start slowly and consult doctor if new to exercise"""
    
    # Sleep and Rest
    elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired', 'fatigue']):
        return """😴 *Sleep Health*

*Recommended Duration:*
• Adults: 7-9 hours
• Teenagers: 8-10 hours
• Children: 9-12 hours
• Preschoolers: 10-13 hours

*Sleep Hygiene:*
• Consistent sleep schedule
• Dark, quiet, cool bedroom
• No screens before bed
• Relaxing bedtime routine

💡 Consult doctor for persistent sleep issues"""
    
    # Greetings
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'namaste']):
        return """👋 Hello! I'm your Health Assistant. I can help with:

💉 Vaccine information
🤒 Symptom checking  
🥗 Diet & nutrition
🛡 Disease prevention
🏥 Health facilities

What would you like to know?

💡 Try: vaccines, symptoms, diet, or prevention"""
    
    # Default comprehensive response
    else:
        return """👋 **Health Assistant**

I can help you with comprehensive health information including:

💉 *Vaccines:* COVID-19, flu, MMR, HPV, travel vaccines
🩺 *Diseases:* Diabetes, hypertension, asthma, heart conditions
🥗 *Diets:* General healthy eating, weight management, meal plans, condition-specific diets
🛡️ *Prevention:* Heart disease, cancer, diabetes prevention
🤒 *Symptoms:* Fever, headache, cough, pain management
💪 *Lifestyle:* Exercise, nutrition, sleep, stress management

What specific health topic would you like to know about?"""



def get_quick_suggestions(message):
    """Add text-based quick suggestions to responses"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['diet', 'food', 'nutrition', 'eat', 'meal']):
        return "\n\n💡 *Quick options:* Type 'meal plans', 'weight management', or 'diet for conditions'"
    
    elif any(word in message_lower for word in ['vaccine', 'vaccination', 'covid']):
        return "\n\n💡 *Quick options:* Type 'covid vaccine', 'child vaccines', or 'travel vaccines'"
    
    elif any(word in message_lower for word in ['symptom', 'pain', 'fever', 'headache', 'cough']):
        return "\n\n💡 *Quick options:* Type 'common symptoms', 'emergency signs', or 'find doctor'"
    
    elif any(word in message_lower for word in ['prevention', 'prevent', 'avoid']):
        return "\n\n💡 *Quick options:* Type 'disease prevention', 'vaccine prevention', or 'healthy lifestyle'"
    
    else:
        return "\n\n💡 Need more help? Try: vaccines, symptoms, diet, or prevention"

def get_simple_fallback_response(message):
    """Simple fallback responses"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "👋 Hello! I'm your Health Assistant. How can I help you today?"
    else:
        return """👋 Hello! I'm your Health Assistant. I can help with:

💉 Vaccine information
🤒 Symptom checking  
🥗 Diet & nutrition
🛡 Disease prevention
🏥 Health facilities

What would you like to know?

💡 Try: vaccines, symptoms, diet, or prevention"""



def send_whatsapp_message(to_number, message_body):
    """
    Send proactive WhatsApp messages to users
    """
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{to_number}"
        )
        print(f'WhatsApp message sent successfully! SID: {message.sid}')
        return message.sid
    except Exception as e:
        print(f'Error sending WhatsApp message: {str(e)}')
        return None

@csrf_exempt
@login_required
def send_whatsapp_message_view(request):
    """
    API endpoint to send WhatsApp messages (for testing from web)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            to_number = data.get('to')
            message = data.get('message')
            
            if not to_number or not message:
                return JsonResponse({'error': 'Missing phone number or message'}, status=400)
            
            message_sid = send_whatsapp_message(to_number, message)
            
            if message_sid:
                return JsonResponse({'status': 'success', 'message_sid': message_sid})
            else:
                return JsonResponse({'error': 'Failed to send message'}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def whatsapp_test(request):
    """
    Test page for WhatsApp integration
    """
    return render(request, 'whatsapp_test.html')

@login_required
def whatsapp_broadcast(request):
    """
    Send health alerts to multiple users
    """
    if request.method == 'POST':
        message = request.POST.get('message')
        numbers = request.POST.get('numbers', '').split(',')
        
        results = []
        for number in numbers:
            number = number.strip()
            if number:
                sid = send_whatsapp_message(number, message)
                results.append({'number': number, 'status': 'success' if sid else 'failed'})
        
        messages.success(request, f'Broadcast sent to {len(results)} numbers')
        return render(request, 'whatsapp_broadcast.html', {'results': results})
    
    return render(request, 'whatsapp_broadcast.html')

# Feature 1: User Session Management
user_sessions = {}

def get_user_session(user_id):
    """Get or create user session"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation_history': [],
            'preferences': {},
            'language': 'en',
            'last_interaction': datetime.now()
        }
    return user_sessions[user_id]

def process_whatsapp_message_with_session(message, user_id, language='en'):
    """Process message with session context"""
    session = get_user_session(user_id)
    
    # Update session
    session['conversation_history'].append({
        'timestamp': datetime.now(),
        'user_message': message,
        'language': language
    })
    session['language'] = language
    session['last_interaction'] = datetime.now()
    
    # Keep only last 10 messages
    if len(session['conversation_history']) > 10:
        session['conversation_history'] = session['conversation_history'][-10:]
    
    # Get context from conversation history
    context = " ".join([msg['user_message'] for msg in session['conversation_history'][-3:]])
    
    # Process with context
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/chatbot/",
            json={
                "message": message,
                "user_id": user_id,
                "language": language,
                "context": context
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            replies = data.get('replies', ['I apologize, but I cannot process that right now.'])
            return "\n".join(replies)
        else:
            return get_fallback_response(message, language)
            
    except Exception as e:
        print(f"Chatbot processing error: {str(e)}")
        return get_fallback_response(message, language)

# Feature 2: Media Support
def handle_media_message(media_url, user_id):
    """Handle image/document uploads"""
    try:
        # For now, provide a response about media handling
        # In production, you would download and process the media
        return "📎 Thank you for sharing! I've received your file. Currently I can help you with:\n\n• Health information\n• Symptom checking\n• Vaccine details\n• Diet advice\n\nPlease describe your health concern in text."
    except Exception as e:
        print(f"Media handling error: {str(e)}")
        return "I received your file but couldn't process it. Please describe your health concern in text."

# Feature 3: Quick Reply Buttons


def add_main_menu_quick_replies(response):
    """Add main menu quick replies"""
    response.message("").button("💉 Vaccines", "vaccines")
    response.message("").button("🤒 Symptoms", "symptoms")
    response.message("").button("🥗 Diet", "diet")
    response.message("").button("🏥 Find Help", "find help")

# Feature 4: Location-Based Services
def handle_location_message(latitude, longitude, user_id):
    """Handle location sharing and find nearby services"""
    try:
        # Store user location in session
        session = get_user_session(user_id)
        session['location'] = {
            'latitude': float(latitude),
            'longitude': float(longitude)
        }
        
        # In production, integrate with Google Maps API or similar
        # For now, provide static information
        return """📍 Thank you for sharing your location! Based on your area, I can help you find:

🏥 Nearby Hospitals: 5 within 5km
💊 Pharmacies: 8 within 3km  
🩺 Clinics: 12 within 4km

Please tell me what you need:
• "Find hospitals" - Nearest medical centers
• "Find pharmacies" - Medicine stores
• "Emergency" - Emergency contacts"""
        
    except Exception as e:
        print(f"Location handling error: {str(e)}")
        return "📍 Thank you for sharing your location! I can help you find nearby health services."

# Feature 6: Multilingual Support
def detect_user_language(message):
    """Simple language detection based on keywords"""
    hindi_keywords = ['नमस्ते', 'धन्यवाद', 'कैसे', 'स्वासth', 'वैक्सीन']
    odia_keywords = ['ନମସ୍କାର', 'ଧନ୍ୟବାଦ', 'କେମିତି', 'ସ୍ୱାସ୍ଥ୍ୟ', 'ଟିକା']
    
    if any(keyword in message for keyword in hindi_keywords):
        return 'hi'
    elif any(keyword in message for keyword in odia_keywords):
        return 'or'
    else:
        return 'en'

def get_welcome_message(user_id):
    """Get welcome message in user's language"""
    session = get_user_session(user_id)
    language = session.get('language', 'en')
    
    welcome_messages = {
        'en': """👋 Hello! I'm your Health Assistant. I can help you with:

💉 Vaccine information
🤒 Symptom checking  
🥗 Diet & nutrition
🏥 Health facilities
🦠 Disease prevention

What would you like to know?""",
        
        'hi': """👋 नमस्ते! मैं आपका स्वास्थ्य सहायक हूं। मैं आपकी मदद कर सकता हूं:

💉 वैक्सीन जानकारी
🤒 लक्षण जांच
🥗 आहार और पोषण
🏥 स्वास्थ्य सुविधाएं
🦠 बीमारी की रोकथाम

आप क्या जानना चाहेंगे?""",
        
        'or': """👋 ନମସ୍କାର! ମୁଁ ଆପଣଙ୍କର ସ୍ୱାସ୍ଥ୍ୟ ସହାୟକ। ମୁଁ ଆପଣଙ୍କୁ ସାହାଯ୍ୟ କରିପାରିବି:

💉 ଟିକା ସୂଚନା
🤒 ଲକ୍ଷଣ ଯାଞ୍ଚ
🥗 ଖାଦ୍ୟ ଏବଂ ପୋଷଣ
🏥 ସ୍ୱାସ୍ଥ୍ୟ ସୁବିଧା
🦠 ରୋଗ ପ୍ରତିରୋଧ

ଆପଣ କ’ଣ ଜାଣିବାକୁ ଚାହାଁନ୍ତି?"""
    }
    
    return welcome_messages.get(language, welcome_messages['en'])

def get_fallback_response(message, language='en'):
    """Get fallback response in appropriate language"""
    fallback_responses = {
        'en': "I'm here to help with health information! Ask me about vaccines, symptoms, or health tips.",
        'hi': "मैं स्वास्थ्य जानकारी में मदद करने के लिए यहां हूं! मुझसे वैक्सीन, लक्षण या स्वास्थ्य युक्तियों के बारे में पूछें।",
        'or': "ମୁଁ ସ୍ୱାସ୍ଥ୍ୟ ସୂଚନାରେ ସାହାଯ୍ୟ କରିବାକୁ ଏଠାରେ ଅଛି! ମୋତେ ଟିକା, ଲକ୍ଷଣ କିମ୍ବା ସ୍ୱାସ୍ଥ୍ୟ ଟିପ୍ସ ବିଷୟରେ ପଚାରନ୍ତୁ।"
    }
    
    return fallback_responses.get(language, fallback_responses['en'])

def add_quick_replies(response, message):
    """Add quick reply buttons based on message context - CORRECT VERSION"""
    message_lower = message.lower()
    
    # For WhatsApp, we need to use the message().button() method correctly
    if any(word in message_lower for word in ['diet', 'food', 'nutrition', 'eat']):
        # Create a new message with buttons
        msg = response.message("Need more specific help?")
        msg.button("Meal Plans", "meal plans")
        msg.button("Weight Management", "weight management")
        msg.button("Diet for Conditions", "diet for conditions")
    
    elif any(word in message_lower for word in ['vaccine', 'vaccination', 'covid']):
        msg = response.message("Which vaccine information?")
        msg.button("COVID-19", "covid vaccine")
        msg.button("Child Vaccines", "child vaccines")
        msg.button("Travel Vaccines", "travel vaccines")
    
    elif any(word in message_lower for word in ['symptom', 'pain', 'fever', 'headache']):
        msg = response.message("What do you need?")
        msg.button("Common Symptoms", "common symptoms")
        msg.button("Emergency Signs", "emergency signs")
        msg.button("Find Doctor", "find doctor")
    
    elif any(word in message_lower for word in ['prevention', 'prevent']):
        msg = response.message("Prevention topics:")
        msg.button("Disease Prevention", "disease prevention")
        msg.button("Vaccine Prevention", "vaccine prevention")
        msg.button("Healthy Lifestyle", "healthy lifestyle")


def add_list_message(response, message):
    """Add list message for better WhatsApp experience"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['diet', 'food', 'nutrition', 'eat']):
        msg = response.message("🍽️ Diet & Nutrition Options:")
        # List messages work better in WhatsApp
        return "🍽️ *Diet & Nutrition Options:*\n\n• Type 'meal plans' for diet plans\n• Type 'weight management' for weight tips\n• Type 'diet for conditions' for specific health conditions\n\nJust type what you need!"
    
    elif any(word in message_lower for word in ['vaccine', 'vaccination', 'covid']):
        return "💉 *Vaccine Information:*\n\n• Type 'covid vaccine' for COVID-19 info\n• Type 'child vaccines' for children vaccination\n• Type 'travel vaccines' for travel requirements\n\nType your choice!"
    
    elif any(word in message_lower for word in ['symptom', 'pain', 'fever', 'headache']):
        return "🤒 *Symptom Help:*\n\n• Type 'common symptoms' for general info\n• Type 'emergency signs' for urgent care\n• Type 'find doctor' for medical help\n\nWhat do you need?"
    
    elif any(word in message_lower for word in ['prevention', 'prevent']):
        return "🛡️ *Prevention Topics:*\n\n• Type 'disease prevention' for illness prevention\n• Type 'vaccine prevention' for vaccine info\n• Type 'healthy lifestyle' for wellness tips\n\nChoose a topic!"
    
    return None


