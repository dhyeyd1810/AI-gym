import json
import os
import random
import math
from typing import Optional, List, Dict
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="AI Gym & Fitness Assistant API",
    description="Multi-module AI and IoT backend for fitness tracking, pose analytics, and smart recommendations.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = os.path.join(os.path.dirname(__file__), "workout_log.json")

def load_logs() -> Dict:
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_logs(data: Dict):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =============================================================================
# REQUEST / RESPONSE SCHEMAS
# =============================================================================

class BMIRequest(BaseModel):
    name: str = "User"
    age: int = 25
    height_cm: float
    weight_kg: float
    goal: str = "maintain"  # lose, gain, maintain

class WorkoutLogRequest(BaseModel):
    user_id: str = "user1"
    completed: bool = True

class PerformanceRequest(BaseModel):
    exercise: str = "Squats"
    total_reps: int
    correct_reps: int
    duration_minutes: float

class ChatRequest(BaseModel):
    message: str
    streak: int = 0

# =============================================================================
# 1. ROOT & HEALTH CHECK
# =============================================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AI Gym & Fitness Assistant API",
        "modules": [
            "AI Gym Trainer (Pose Detection)",
            "AI Dietician (BMI & Macro Planning)",
            "Smart Gym (IoT Simulator)",
            "Habit Tracker & Skip Risk Predictor",
            "Virtual Gym Buddy Chat",
            "Performance & Form Analyzer",
            "Gym & Workout Recommender"
        ]
    }

# =============================================================================
# 2. MODULE: AI DIETICIAN (BMI & DIET PLANNER)
# =============================================================================

@app.post("/bmi")
def calculate_bmi(req: BMIRequest):
    if req.height_cm <= 0 or req.weight_kg <= 0:
        raise HTTPException(status_code=400, detail="Height and weight must be greater than zero.")
    
    height_m = req.height_cm / 100.0
    bmi = round(req.weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 24.9:
        category = "Normal"
    elif 25.0 <= bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"

    # Base metabolic estimate + adjustment based on goal
    bmr = 10 * req.weight_kg + 6.25 * req.height_cm - 5 * req.age + 5
    tdee = bmr * 1.35  # Moderately active baseline

    goal_key = req.goal.lower()
    if "lose" in goal_key:
        target_calories = int(tdee - 450)
        diet_plan = {
            "calories": target_calories,
            "breakfast": "Oatmeal with chia seeds, blueberries, and whey protein isolate",
            "lunch": "Grilled chicken breast or tofu bowl with quinoa and steamed broccoli",
            "dinner": "Pan-seared salmon or paneer salad with avocado and olive oil dressing"
        }
    elif "gain" in goal_key:
        target_calories = int(tdee + 400)
        diet_plan = {
            "calories": target_calories,
            "breakfast": "4 whole eggs, whole grain toast with peanut butter and banana shake",
            "lunch": "Brown rice with chicken thigh or paneer tikka, mixed lentils and spinach",
            "dinner": "Sweet potato mash, lean steak or soybean curry with Greek yogurt"
        }
    else:
        target_calories = int(tdee)
        diet_plan = {
            "calories": target_calories,
            "breakfast": "Scrambled eggs with spinach, avocado toast, and green tea",
            "lunch": "Mediterranean grain bowl with chickpeas, feta cheese, and grilled veggies",
            "dinner": "Grilled fish or tofu stir-fry with jasmine rice and bell peppers"
        }

    return {
        "name": req.name,
        "bmi": bmi,
        "category": category,
        "target_calories": target_calories,
        "diet_plan": diet_plan
    }

# =============================================================================
# 3. MODULE: HABIT TRACKER & SKIP RISK PREDICTOR
# =============================================================================

@app.post("/log-workout")
def log_workout(req: WorkoutLogRequest):
    logs = load_logs()
    user_data = logs.get(req.user_id, {"streak": 0, "history": []})
    
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if req.completed:
        user_data["streak"] += 1
        # Lower skip risk as streak builds
        skip_risk = max(0.05, round(0.55 * (0.85 ** min(user_data["streak"], 10)), 2))
        motivation = random.choice([
            "Unstoppable momentum! Consistency is what transforms goals into reality.",
            "Crushed it today! Every rep brings you closer to your personal best.",
            "Phenomenal work! Keep the streak burning bright."
        ])
    else:
        user_data["streak"] = 0
        skip_risk = 0.75
        motivation = "Rest days happen, but don't let one miss become two! Get back stronger tomorrow."

    user_data["history"].append({
        "timestamp": today_str,
        "completed": req.completed,
        "streak_at_time": user_data["streak"]
    })
    
    logs[req.user_id] = user_data
    save_logs(logs)

    return {
        "user_id": req.user_id,
        "streak": user_data["streak"],
        "skip_risk": skip_risk,
        "motivation": motivation
    }

@app.get("/workout-history/{user_id}")
def get_workout_history(user_id: str):
    logs = load_logs()
    user_data = logs.get(user_id, {"streak": 0, "history": []})
    return {
        "user_id": user_id,
        "streak": user_data.get("streak", 0),
        "history": user_data.get("history", [])
    }

# =============================================================================
# 4. MODULE: IOT SMART GYM EQUIPMENT SIMULATOR
# =============================================================================

@app.get("/equipment-status")
def get_equipment_status():
    heart_rate = random.randint(115, 172)
    resistance_level = random.randint(4, 12)
    calories_burned = random.randint(180, 520)

    if heart_rate > 160:
        recommendation = "Heart rate in Peak Zone. Lower resistance by 2 levels and maintain hydration."
    elif heart_rate < 120:
        recommendation = "Heart rate in Warm-up Zone. Increase pace or resistance to enter Cardio Target Zone."
    else:
        recommendation = "Heart rate in Optimal Aerobic Zone. Maintain cadence for peak fat burn."

    return {
        "heart_rate": heart_rate,
        "resistance_level": resistance_level,
        "calories_burned": calories_burned,
        "equipment_online": True,
        "recommendation": recommendation
    }

# =============================================================================
# 5. MODULE: WORKOUT PERFORMANCE ANALYZER
# =============================================================================

@app.post("/performance-score")
def analyze_performance(req: PerformanceRequest):
    if req.total_reps <= 0:
        raise HTTPException(status_code=400, detail="Total reps must be greater than 0.")
    
    correct = min(req.correct_reps, req.total_reps)
    accuracy_pct = round((correct / req.total_reps) * 100, 1)

    # Rep pacing efficiency (standard target ~3-4 sec per rep)
    expected_duration = (req.total_reps * 3.5) / 60.0  # in minutes
    if req.duration_minutes > 0:
        pace_ratio = expected_duration / req.duration_minutes
        efficiency_pct = min(100, max(40, round(pace_ratio * 90, 1)))
    else:
        efficiency_pct = 85.0

    score = int((accuracy_pct * 0.7) + (efficiency_pct * 0.3))

    if score >= 85:
        grade = "Excellent"
    elif score >= 70:
        grade = "Good"
    elif score >= 50:
        grade = "Average"
    else:
        grade = "Needs Improvement"

    return {
        "exercise": req.exercise,
        "performance_score": score,
        "grade": grade,
        "accuracy_pct": accuracy_pct,
        "efficiency_pct": efficiency_pct
    }

# =============================================================================
# 6. MODULE: GYM & PROGRAM RECOMMENDER
# =============================================================================

@app.get("/recommend/{goal}")
def get_recommendations(goal: str):
    gyms = [
        {"name": "Iron Elite Fitness Center", "rating": 4.9},
        {"name": "Pulse Crossfit & Functional Arena", "rating": 4.8},
        {"name": "Zenith Wellness & Strength Club", "rating": 4.7},
        {"name": "Anytime Powerhouse Gym", "rating": 4.6}
    ]

    g = goal.lower()
    if "lose" in g:
        programs = [
            "HIIT & Circuit Training (4x / week)",
            "Zone 2 Cardio + Full Body Calisthenics",
            "Tabata Kettlebell Fat-Loss Protocol"
        ]
    elif "gain" in g:
        programs = [
            "Push-Pull-Legs (PPL) Hypertrophy Split (6x / week)",
            "Upper / Lower Strength Progression (4x / week)",
            "Compound Heavy 5x5 Power-Building"
        ]
    else:
        programs = [
            "Functional Mobility & Resistance Hybrid (3x / week)",
            "Full Body Moderate Kettlebell Conditioning",
            "Cardio-Core Balance Routine"
        ]

    return {
        "goal": goal,
        "nearby_gyms": gyms,
        "suggested_programs": programs
    }

# =============================================================================
# 7. MODULE: VIRTUAL GYM BUDDY (AI CHAT COMPANION)
# =============================================================================

@app.post("/chat")
def chat_buddy(req: ChatRequest):
    msg = req.message.lower()

    if "tired" in msg or "exhausted" in msg or "lazy" in msg:
        reply = "I hear you! Remember: the hardest part is just putting on your shoes. Even a light 15-minute session counts!"
    elif "diet" in msg or "eat" in msg or "food" in msg or "protein" in msg:
        reply = "Aim for 1.6 - 2.2g of protein per kg of body weight, drink 3-4 liters of water, and keep processed sugars low!"
    elif "sore" in msg or "pain" in msg:
        reply = "Listen to your body. Active recovery (foam rolling, walking, light stretching) works wonders for DOMS."
    elif "squat" in msg or "form" in msg or "bench" in msg or "deadlift" in msg:
        reply = "Keep your core braced, maintain a neutral spine, and control both the concentric and eccentric phases."
    else:
        reply = "You've got this! Focus on progressive overload, good form, and solid sleep. Let's make every rep count!"

    if req.streak >= 7:
        streak_message = f"🔥 Legendary {req.streak}-day streak! You are in the top tier of consistency!"
    elif req.streak >= 3:
        streak_message = f"⚡ Great momentum on your {req.streak}-day streak! Keep pushing forward!"
    elif req.streak > 0:
        streak_message = f"🌱 Day {req.streak} logged! A great habit is forming."
    else:
        streak_message = "Ready to start day 1 of your streak today? Let's do it!"

    return {
        "reply": reply,
        "streak_message": streak_message
    }
