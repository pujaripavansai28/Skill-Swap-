# core/views.py

import google.generativeai as genai
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from .forms import CustomUserCreationForm, ProfileForm
from .models import Profile, Skill, SwapRequest
from django.contrib.auth.models import User

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# The homepage view from Phase 1
def home(request):
    # If the user is already logged in, don't show them the marketing page.
    # Redirect them straight to the dashboard.
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Otherwise, show the new landing page.
    return render(request, 'home.html')

# Signup View
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a profile for the new user automatically
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('profile') # Redirect to profile page to complete setup
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# core/views.py

# Add these imports at the top
from .forms import ProfileForm, AddSkillForm 
from .models import UserSkill, SwapRequest, Review # Make sure all models are imported

# --- REPLACE YOUR OLD profile VIEW WITH THIS ---
@login_required
def profile(request):
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    user = request.user

    # Handle the "Add Skill" form submission
    if 'add_skill' in request.POST:
        add_skill_form = AddSkillForm(request.POST)
        if add_skill_form.is_valid():
            skill_to_add = add_skill_form.cleaned_data['skill']
            UserSkill.objects.get_or_create(user_profile=profile_obj, skill=skill_to_add)
            messages.success(request, f"Skill '{skill_to_add.name}' added to your profile!")
            return redirect('profile')
    else:
        add_skill_form = AddSkillForm()

    # Handle the main profile form submission
    if 'update_profile' in request.POST:
        profile_form = ProfileForm(request.POST, instance=profile_obj)
        if profile_form.is_valid():
            # --- START OF FIX ---
            # Step 1: Save the form's data to a temporary object without committing to the database.
            # This allows us to modify it before the final save.
            temp_profile = profile_form.save(commit=False)
            
            # Step 2: Manually handle the availability checkboxes because we overrode the field.
            availability_list = profile_form.cleaned_data.get('availability', [])
            temp_profile.availability = ', '.join(availability_list)
            
            # Step 3: Now, save the main object to the database.
            temp_profile.save()
            
            # Step 4: Because we used commit=False, we must now explicitly save the many-to-many data.
            # This is where the save_m2m() method is correctly used.
            profile_form.save_m2m()
            # --- END OF FIX ---

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        # Populate form with existing data
        initial_data = {'availability': profile_obj.availability.split(', ') if profile_obj.availability else []}
        profile_form = ProfileForm(instance=profile_obj, initial=initial_data)

    # --- Gamification and Badge Logic (this part remains the same) ---
    completeness_score = 0
    if profile_obj.location: completeness_score += 25
    if profile_obj.availability: completeness_score += 25
    if profile_obj.userskill_set.exists(): completeness_score += 25
    if profile_obj.skills_wanted.exists(): completeness_score += 25
    
    earned_badges = []
    # Badge 1: Profile Pro
    if completeness_score == 100:
        earned_badges.append({'name': 'Profile Pro', 'icon': 'bi-person-check-fill', 'description': 'Your profile is 100% complete!'})
    # Badge 2: First Swap
    if SwapRequest.objects.filter(Q(requester=user) | Q(responder=user), status='completed').exists():
        earned_badges.append({'name': 'First Swap', 'icon': 'bi-award-fill', 'description': 'Congratulations on completing your first skill swap!'})
    # Badge 3: Top Rated
    if Review.objects.filter(reviewee=user, rating=5).exists():
        earned_badges.append({'name': 'Top Rated', 'icon': 'bi-star-fill', 'description': 'You received a 5-star rating!'})
    # Badge 4: Super Swapper
    if SwapRequest.objects.filter(Q(requester=user) | Q(responder=user), status='completed').count() >= 5:
        earned_badges.append({'name': 'Super Swapper', 'icon': 'bi-trophy-fill', 'description': 'You have completed 5 or more swaps!'})
    
    context = {
        'profile_form': profile_form,
        'add_skill_form': add_skill_form,
        'profile_completeness_score': completeness_score,
        'earned_badges': earned_badges,
    }
    return render(request, 'profile.html', context)

# AI Skill Suggester View
@login_required
def suggest_skills(request):
    # Get the user's input from the request
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({'suggestions': []})

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"Based on the skill '{query}', suggest 5 related or more professional-sounding skills. Return your answer as a simple comma-separated list. Example: 'Data Analysis,Spreadsheet Management,Financial Modeling,Data Visualization,Business Intelligence'"
        
        response = model.generate_content(prompt)
        suggestions = [s.strip() for s in response.text.split(',')]
        
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        # In case of API error, return an empty list
        return JsonResponse({'suggestions': [], 'error': str(e)})


# core/views.py

# Add these imports at the top of the file
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages
from .models import SwapRequest 

# --- Add the new views below your existing ones ---
@login_required
def browse_users(request):
    skill_query = request.GET.get('q', '')
    location_query = request.GET.get('location', '') # Get location from URL
    
    profiles = Profile.objects.filter(is_public=True).exclude(user=request.user)

    if skill_query:
        profiles = profiles.filter(skills_offered__name__icontains=skill_query).distinct()
    
    if location_query:
        profiles = profiles.filter(location__icontains=location_query) # Add location filter
    
    context = {
        'profiles': profiles,
        'search_query': skill_query,
        'location_query': location_query # Pass location back to template
    }
    return render(request, 'browse_users.html', context)

@login_required
def user_public_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    
    swap_exists = SwapRequest.objects.filter(
        (Q(requester=request.user, responder=profile_user) | Q(requester=profile_user, responder=request.user))
    ).exists()

    # --- NEW: Fetch recent reviews for this user ---
    reviews = Review.objects.filter(reviewee=profile_user).order_by('-created_at')[:3]
    # --- End New ---

    context = {
        'profile_user': profile_user,
        'swap_exists': swap_exists,
        'reviews': reviews, # Pass reviews to the template
    }
    return render(request, 'user_public_profile.html', context)

@login_required
def send_swap_request(request, user_id):
    # This view only handles POST requests for security
    if request.method == 'POST':
        responder = get_object_or_404(User, id=user_id)
        # Prevent users from sending requests to themselves
        if responder != request.user:
            # Create the swap request object
            SwapRequest.objects.get_or_create(
                requester=request.user,
                responder=responder,
                defaults={'status': 'pending'}
            )
            messages.success(request, f"Your swap request to {responder.username} has been sent!")
        else:
            messages.error(request, "You cannot send a swap request to yourself.")
    return redirect('dashboard') # Redirect to dashboard to see the new request
@login_required
def swap_dashboard(request):
    # --- AI Matcher Logic for Dashboard ---
    ai_suggestions = []
    try:
        current_user_profile = request.user.profile
        user_skills_offered = list(current_user_profile.skills_offered.values_list('name', flat=True))
        user_skills_wanted = list(current_user_profile.skills_wanted.values_list('name', flat=True))
        
        # Get a sample of other public profiles to keep it fast
        candidate_profiles = Profile.objects.filter(is_public=True).exclude(user=request.user).order_by('-user__last_login')[:10]
        
        if candidate_profiles:
            candidates_data = [{
                "user_id": p.user.id,
                "skills_offered": list(p.skills_offered.values_list('name', flat=True)),
                "skills_wanted": list(p.skills_wanted.values_list('name', flat=True))
            } for p in candidate_profiles]

            prompt = f"Find the top 3 best swap matches for user '{request.user.username}' who offers {user_skills_offered} and wants {user_skills_wanted}, from this list: {json.dumps(candidates_data)}. Prioritize direct swaps. Return ONLY a valid JSON array of objects with keys: 'user_id', 'justification'."
            
            model = genai.GenerativeModel('gemini-pro')
            safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
            response = model.generate_content(prompt, safety_settings=safety_settings)
            
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            ai_matches_data = json.loads(raw_text)

            for match_data in ai_matches_data:
                try:
                    user_obj = User.objects.get(id=match_data.get('user_id'))
                    ai_suggestions.append({'user': user_obj, 'justification': match_data.get('justification')})
                except User.DoesNotExist:
                    continue
    except Exception as e:
        # If AI fails, we don't crash the page. The dashboard still works.
        print(f"AI Dashboard Matcher Error: {e}") 

    # --- End AI Matcher ---

    incoming_requests = SwapRequest.objects.filter(responder=request.user, status='pending')
    sent_requests = SwapRequest.objects.filter(requester=request.user).exclude(status__in=['completed', 'accepted'])
    active_swaps = SwapRequest.objects.filter(Q(requester=request.user) | Q(responder=request.user), status='accepted')
    completed_swaps = SwapRequest.objects.filter(Q(requester=request.user) | Q(responder=request.user), status='completed').order_by('-updated_at')

    context = {
        'ai_suggestions': ai_suggestions, # Add suggestions to context
        'incoming_requests': incoming_requests,
        'sent_requests': sent_requests,
        'active_swaps': active_swaps,
        'completed_swaps': completed_swaps,
    }
    return render(request, 'swap_dashboard.html', context)

@login_required
def update_swap_status(request, request_id, new_status):
    # This view also only handles POST requests
    if request.method == 'POST':
        swap_request = get_object_or_404(SwapRequest, id=request_id)
        
        # Security Check: Only the responder can accept/reject
        if swap_request.responder == request.user and new_status in ['accepted', 'rejected']:
            swap_request.status = new_status
            swap_request.save()
            messages.success(request, f"Swap request has been {new_status}.")
        # Allow the requester to cancel a pending request
        elif swap_request.requester == request.user and new_status == 'cancelled' and swap_request.status == 'pending':
            swap_request.status = new_status
            swap_request.save()
            messages.info(request, "You have cancelled the swap request.")
        else:
            messages.error(request, "You do not have permission to perform this action.")
            
    return redirect('dashboard')


# core/views.py

# Add this import at the top of the file if it's not already there
import json

# --- Add the new view below your existing ones ---

@login_required
def ai_matchmaker(request):
    current_user_profile = request.user.profile
    api_error = None
    matches = []

    # 1. GATHER CONTEXT
    user_skills_offered = list(current_user_profile.skills_offered.values_list('name', flat=True))
    user_skills_wanted = list(current_user_profile.skills_wanted.values_list('name', flat=True))

    # 2. FETCH CANDIDATES
    candidate_profiles = Profile.objects.filter(is_public=True).exclude(user=request.user)
    
    # 3. FORMAT DATA FOR AI
    candidates_data = []
    for profile in candidate_profiles:
        candidates_data.append({
            "user_id": profile.user.id,
            "skills_offered": list(profile.skills_offered.values_list('name', flat=True)),
            "skills_wanted": list(profile.skills_wanted.values_list('name', flat=True))
        })

    if candidates_data:
        # 4. ENGINEER THE PROMPT (same as before)
        prompt = f"""
        You are an expert matchmaker for a skill-swapping platform. Your task is to find the best matches for a user based on their skills.

        **My User's Profile:**
        - User Name: {request.user.username}
        - Skills They Offer: {user_skills_offered}
        - Skills They Want: {user_skills_wanted}

        **Available Candidates:**
        Here is a list of other users on the platform in JSON format:
        {json.dumps(candidates_data, indent=2)}

        **Your Instructions:**
        1. Analyze the candidates to find the top 3-5 best matches for my user.
        2. A "Direct Swap" is the highest priority (they want what my user offers, and my user wants what they offer).
        3. Also consider "Potential Interest" matches (e.g., they offer something my user wants, even if there's no direct return match).
        4. For each match, provide a `user_id`, a `match_type`, and a one-sentence `justification` explaining WHY it's a good match.
        
        **Return your response ONLY as a valid JSON array of objects, with no other text before or after it.**
        Example format:
        [
          {{
            "user_id": 123,
            "match_type": "Direct Swap",
            "justification": "This is a perfect match because you offer the 'Python' they want, and they offer the 'Guitar Lessons' you're looking for."
          }}
        ]
        """
        
        try:
            # 5. CALL API WITH IMPROVEMENTS
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # --- START OF FIX ---
            # Define safety settings to be more lenient
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            response = model.generate_content(prompt, safety_settings=safety_settings)

            # Add this print statement for debugging. Check your terminal!
            print("--- GEMINI API RESPONSE ---")
            print(response)
            print("---------------------------")
            
            # Now, we robustly access the text to avoid errors
            # The AI might return ```json ... ```, so we clean it
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            ai_matches = json.loads(raw_text)
            # --- END OF FIX ---

            # 6. ENRICH DATA (same as before)
            for match_data in ai_matches:
                try:
                    user_obj = User.objects.get(id=match_data.get('user_id'))
                    matches.append({
                        'user': user_obj,
                        'match_type': match_data.get('match_type', 'N/A'),
                        'justification': match_data.get('justification', 'No justification provided.')
                    })
                except User.DoesNotExist:
                    continue
        except Exception as e:
            api_error = f"Could not get AI suggestions at this time. Error: {str(e)}"

    context = {
        'matches': matches,
        'api_error': api_error,
        'has_candidates': bool(candidates_data)
    }
    return render(request, 'ai_matchmaker.html', context)

# core/views.py

# Add these imports at the top if they are not there
from django.core.exceptions import PermissionDenied
from .forms import ReviewForm
from .models import Review

# --- ADD THIS ENTIRE NEW VIEW AT THE END OF THE FILE ---

@login_required
def leave_review(request, swap_request_id):
    swap = get_object_or_404(SwapRequest, id=swap_request_id)
    user = request.user

    # --- Security & Logic Checks ---
    # 1. Check if the swap is actually completed
    if swap.status != 'completed':
        messages.error(request, "You can only review completed swaps.")
        return redirect('dashboard')

    # 2. Check if the user is part of this swap
    if user != swap.requester and user != swap.responder:
        raise PermissionDenied

    # 3. Determine the person being reviewed (the 'reviewee')
    reviewee = swap.responder if user == swap.requester else swap.requester

    # 4. Check if the user has already left a review
    if (user == swap.requester and swap.requester_reviewed) or \
       (user == swap.responder and swap.responder_reviewed):
        messages.info(request, "You have already submitted a review for this swap.")
        return redirect('dashboard')

    # --- Form Handling ---
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.swap = swap
            review.reviewer = user
            review.reviewee = reviewee
            review.save()

            # Mark that this user has now reviewed the swap
            if user == swap.requester:
                swap.requester_reviewed = True
            else:
                swap.responder_reviewed = True
            swap.save()

            messages.success(request, f"Your review for {reviewee.username} has been submitted!")
            return redirect('dashboard')
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'swap': swap,
        'reviewee': reviewee
    }
    return render(request, 'leave_review.html', context)



@login_required
def generate_skill_quiz(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    quiz_questions = []
    api_error = None

    prompt = f"""
    You are a Skill Assessor AI. Your task is to generate a short, 3-question multiple-choice quiz about the skill: "{skill.name}".
    The quiz should be difficult enough to require genuine knowledge.
    
    For each question, provide:
    - "question": The question text.
    - "options": A list of 4 strings (3 incorrect, 1 correct).
    - "correct_answer": The exact text of the correct option.
    
    Return your response ONLY as a valid JSON array of 3 question objects. Do not include any other text or markdown formatting.
    Example format:
    [
      {{
        "question": "In Python, what is the primary purpose of a 'decorator'?",
        "options": ["To decorate the command line", "To add functionality to an existing function", "To store data", "To create a virtual environment"],
        "correct_answer": "To add functionality to an existing function"
      }}
    ]
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        response = model.generate_content(prompt, safety_settings=safety_settings)
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        quiz_questions = json.loads(raw_text)
        # Store the quiz and correct answers in the user's session to check later
        request.session['skill_quiz'] = quiz_questions
        request.session['quiz_skill_id'] = skill_id
    except Exception as e:
        api_error = f"Could not generate a quiz at this time. Error: {str(e)}"

    context = {
        'skill': skill,
        'quiz_questions': quiz_questions,
        'api_error': api_error,
    }
    return render(request, 'skill_quiz.html', context)

@login_required
def submit_skill_quiz(request):
    if request.method == 'POST':
        user_answers = request.POST
        correct_answers_count = 0
        
        # Retrieve the quiz from the session
        quiz_questions = request.session.get('skill_quiz', [])
        skill_id = request.session.get('quiz_skill_id')

        if not quiz_questions or not skill_id:
            messages.error(request, "Quiz session expired or not found. Please try again.")
            return redirect('profile')

        # Compare user's answers to the stored correct answers
        for i, question_data in enumerate(quiz_questions):
            user_answer = user_answers.get(f'question_{i}')
            if user_answer == question_data['correct_answer']:
                correct_answers_count += 1
        
        # We'll say passing is getting 2 out of 3 correct
        if correct_answers_count >= 2:
            # Update the UserSkill model to mark as verified
            user_skill = get_object_or_404(UserSkill, user_profile=request.user.profile, skill_id=skill_id)
            user_skill.is_verified = True
            user_skill.save()
            messages.success(request, f"Congratulations! You passed the quiz and your '{user_skill.skill.name}' skill is now verified!")
        else:
            messages.error(request, f"You answered {correct_answers_count} out of {len(quiz_questions)} correctly. You did not pass this time. Feel free to try again later.")

        # Clear the quiz from the session
        del request.session['skill_quiz']
        del request.session['quiz_skill_id']

        return redirect('profile')
    
    return redirect('profile') # Redirect if not a POST request


@login_required
def ai_chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if not user_message:
            return JsonResponse({'reply': 'Please ask a question.'})

        # Provide context to the AI
        prompt = f"""
        You are 'SkillSwap Helper', a friendly and helpful AI assistant for the SkillSwap platform.
        Your user, '{request.user.username}', has asked a question.
        
        Answer concisely and helpfully. You can answer general questions about the platform.
        If the user asks to find someone, provide a link they can click in the format '/browse/?q=SKILL'.
        
        User's question: "{user_message}"
        
        Your reply:
        """
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            # Simple text parsing is enough here
            return JsonResponse({'reply': response.text})
        except Exception as e:
            return JsonResponse({'reply': f'Sorry, I encountered an error: {str(e)}'})

    return JsonResponse({'error': 'Invalid request'}, status=400)
