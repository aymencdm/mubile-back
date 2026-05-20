import os
import joblib
import pandas as pd
from datetime import datetime
from django.conf import settings


def calculate_water_goal(weight, age=None, gender=None, activity="Moderate", weather="Normal", exercise_minutes=0):
    """
    حساب الهدف اليومي للماء (EFSA & ACSM)
    1. Base = weight * 35
    2. Activity multiplier: Low=1.10, Moderate=1.20, High=1.50
    3. Climate extra: Hot=+500
    4. Exercise extra: (exercise_minutes / 30) * 400
    5. Multiply by 0.80 (80% from drinks, 20% from food)
    6. Clamp between 1500 and 5000
    """
    if weight is None or weight <= 0:
        weight = 70

    # 1. Base
    goal = weight * 35

    # 2. Activity Multiplier
    activity_multiplier = {"Low": 1.10, "Moderate": 1.20, "High": 1.50}.get(activity, 1.20)
    goal = goal * activity_multiplier

    # 3. Climate Extra
    climate_extra = {"Cold": 0, "Normal": 0, "Hot": 500}.get(weather, 0)
    goal += climate_extra

    # 4. Exercise Extra
    exercise_extra = (exercise_minutes / 30.0) * 400
    goal += exercise_extra

    # 5. Food factor (80% drinks)
    goal = goal * 0.80

    # 6. Clamp
    goal = max(goal, 1500)
    goal = min(goal, 5000)

    # 9. Return rounded integer
    return round(goal)


def temperature_to_weather(ambient_temperature):
    """
    تحويل درجة حرارة الهواء (DHT22) إلى weather category
    < 15°C  → Cold
    15-30°C → Normal
    > 30°C  → Hot
    """
    if ambient_temperature is None:
        return "Normal"
    if ambient_temperature < 15:
        return "Cold"
    elif ambient_temperature > 30:
        return "Hot"
    else:
        return "Normal"


def get_time_of_day():
    """
    تحويل الساعة الحالية إلى فئة Time_of_Day
    بناءً على الـ Skin dataset: 1=Morning, 2=Afternoon, 3=Evening
    """
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return 1  # Morning
    elif 12 <= hour < 18:
        return 2  # Afternoon
    else:
        return 3  # Evening


def predict_hydration(age, weight, gender, activity, weather, water_consumed_liters):
    """
    Body hydration prediction من body_hydration_model.pkl
    Dataset target: Good / Poor
    Returns: (status, confidence)
    - status: "Hydrated" (Good) | "Dehydrated" (Poor)
    - confidence: AI confidence % (0-100)
    ملاحظة: Warning يُحسب من calculate_body_percentage() وليس من الـ model
    """
    model_path = os.path.join(
        settings.BASE_DIR, "core", "models", "body_hydration_model.pkl"
    )

    if not os.path.exists(model_path):
        print("⚠️ [BODY] Model not found at:", model_path)
        return "Dehydrated", 0.0

    try:
        model = joblib.load(model_path)

        data = {
            "Gender":             gender,
            "Physical_Activity":  activity,
            "Weather":            weather,
            "Age":                age,
            "Weight":             weight,
            "Daily_Water_Intake": water_consumed_liters
        }

        df = pd.DataFrame([data])

        print(f"[BODY] Model type  : {type(model).__name__}")
        print(f"[BODY] Input data  : {data}")

        prediction = model.predict(df)[0]
        print(f"[BODY] Raw prediction: {prediction}")

        # Good → Hydrated | Poor → Dehydrated
        status = "Hydrated" if str(prediction).lower() == "good" else "Dehydrated"
        print(f"[BODY] Status: {status}")

        # Confidence
        confidence = 0.0
        if hasattr(model, 'predict_proba'):
            try:
                proba = model.predict_proba(df)[0]
                classes = list(model.classes_)
                print(f"[BODY] Classes: {classes} | Proba: {proba}")
                confidence = round(float(max(proba)) * 100, 1)
            except Exception as e:
                print(f"[BODY] predict_proba error: {e}")
                confidence = 75.0
        else:
            print("[BODY] No predict_proba — using fallback confidence")
            confidence = 80.0 if status == "Hydrated" else 65.0

        print(f"[BODY] Confidence: {confidence}%")
        return status, confidence

    except Exception as e:
        print(f"[BODY] Critical error: {e}")
        return "Dehydrated", 0.0


def calculate_body_percentage(water_consumed_ml, recommended_goal_ml):
    """
    Body Hydration % = (consumed / goal) × 100
    مقيد بـ 0-100%
    """
    if recommended_goal_ml <= 0:
        return 0.0
    percentage = (water_consumed_ml / recommended_goal_ml) * 100
    return round(min(percentage, 100.0), 1)


def body_status_from_percentage(percentage):
    """
    تحويل النسبة المئوية إلى label:
    >= 75% → Hydrated
    40-75% → Warning
    < 40%  → Dehydrated
    """
    if percentage >= 75:
        return "Hydrated"
    elif percentage >= 40:
        return "Warning"
    else:
        return "Dehydrated"


def predict_skin_hydration(
    electrical_capacitance,
    skin_temperature,
    skin_conductance,
    ambient_humidity,
    ambient_temperature,
    time_of_day
):
    """
    Skin hydration prediction من skin_model.pkl
    Dataset target: 1=Hydrated, 0=Dehydrated
    Time_of_Day: 1=Morning, 2=Afternoon, 3=Evening
    Returns: (status, confidence, hydration_percentage)
    - status: "Hydrated" | "Dehydrated"
    - confidence: AI confidence % (0-100)
    - hydration_percentage: P(Hydrated) × 100
    """
    model_path = os.path.join(
        settings.BASE_DIR, "core", "models", "skin_model.pkl"
    )

    if not os.path.exists(model_path):
        print("⚠️ [SKIN] Model not found at:", model_path)
        return "Dehydrated", 0.0, 0.0

    try:
        model = joblib.load(model_path)

        data = {
            "Electrical_Capacitance": electrical_capacitance,
            "Skin_Temperature": skin_temperature,
            "Skin_Conductance": skin_conductance,
            "Ambient_Humidity": ambient_humidity,
            "Ambient_Temperature": ambient_temperature,
            "Time_of_Day": time_of_day  # 1, 2, or 3
        }

        df = pd.DataFrame([data])

        print(f"[SKIN] Model type  : {type(model).__name__}")
        print(f"[SKIN] Input data  : {data}")

        prediction = model.predict(df)[0]
        print(f"[SKIN] Raw prediction: {prediction}")

        # 1 → Hydrated | 0 → Dehydrated
        status = "Hydrated" if int(prediction) == 1 else "Dehydrated"
        print(f"[SKIN] Status: {status}")

        confidence = 0.0
        hydration_percentage = 100.0 if status == "Hydrated" else 0.0

        if hasattr(model, 'predict_proba'):
            try:
                proba = model.predict_proba(df)[0]
                classes = list(model.classes_)
                print(f"[SKIN] Classes: {classes} | Proba: {proba}")

                # نأخذ P(class=1) = P(Hydrated)
                if 1 in classes:
                    hydrated_idx = classes.index(1)
                    hydration_percentage = round(
                        float(proba[hydrated_idx]) * 100, 1
                    )
                else:
                    # fallback لو classes مختلفة
                    hydration_percentage = round(float(max(proba)) * 100, 1)
                    if status == "Dehydrated":
                        hydration_percentage = round(
                            100.0 - hydration_percentage, 1
                        )

                confidence = round(float(max(proba)) * 100, 1)

            except Exception as e:
                print(f"[SKIN] predict_proba error: {e}")
                confidence = 75.0
                hydration_percentage = 75.0 if status == "Hydrated" else 25.0
        else:
            print("[SKIN] No predict_proba — using fallback")
            confidence = 80.0 if status == "Hydrated" else 65.0
            hydration_percentage = 80.0 if status == "Hydrated" else 20.0

        print(f"[SKIN] Confidence: {confidence}% | Hydration%: {hydration_percentage}%")
        return status, confidence, hydration_percentage

    except Exception as e:
        print(f"[SKIN] Critical error: {e}")
        return "Dehydrated", 0.0, 0.0


def final_hydration_status(body_status, skin_status):
    """
    Fusion logic:
    Hydrated + Hydrated → Hydrated
    Dehydrated + Dehydrated → Dehydrated
    أي حالة أخرى → Warning
    """
    if body_status == "Hydrated" and skin_status == "Hydrated":
        return "Hydrated"
    elif body_status == "Dehydrated" and skin_status == "Dehydrated":
        return "Dehydrated"
    else:
        return "Warning"


def calculate_final_percentage(body_percentage, skin_percentage):
    """
    Final % = متوسط Body + Skin
    """
    return round((body_percentage + skin_percentage) / 2, 1)


def get_advice(status, percentage=None, body_status=None, skin_status=None,
               remaining_water_ml=None, body_percentage=None, skin_percentage=None):
    """
    نصيحة ذكية بناءً على Body + Skin معاً
    """
    # ── HYDRATED ──────────────────────────────────────────────────────────
    if status == "Hydrated":
        if body_percentage and body_percentage >= 90:
            return (
                "Excellent hydration! 💧 Your body and skin are well hydrated. "
                "Keep drinking water regularly to maintain this level."
            )
        return (
            "Great job! 🌊 You're well hydrated. "
            "Keep up your routine and drink water every 2 hours."
        )

    # ── WARNING ───────────────────────────────────────────────────────────
    elif status == "Warning":
        # Body OK لكن Skin جافة
        if body_status == "Hydrated" and skin_status == "Dehydrated":
            remaining = f"{remaining_water_ml:.0f} ml" if remaining_water_ml else "more water"
            return (
                f"⚠️ Your body hydration is good, but your skin needs attention. "
                f"Drink {remaining} and consider using a moisturizer. "
                f"Avoid direct sunlight and stay in a cool environment."
            )
        # Body جاف لكن Skin OK
        elif body_status == "Dehydrated" and skin_status == "Hydrated":
            remaining = f"{remaining_water_ml:.0f} ml" if remaining_water_ml else "more water"
            return (
                f"⚠️ Your skin is hydrated but your body needs more water. "
                f"Drink {remaining} to reach your daily goal. "
                f"Try to drink a full glass of water right now."
            )
        # كلاهما Warning
        else:
            remaining = f"{remaining_water_ml:.0f} ml" if remaining_water_ml else "more water"
            return (
                f"⚠️ Your hydration level is dropping. "
                f"Drink {remaining} to reach your daily goal. "
                f"Take a break, drink water, and rest in a cool place."
            )

    # ── DEHYDRATED ────────────────────────────────────────────────────────
    else:
        # كلاهما Dehydrated
        if body_status == "Dehydrated" and skin_status == "Dehydrated":
            remaining = f"{remaining_water_ml:.0f} ml" if remaining_water_ml else "water"
            return (
                f"🚨 Critical dehydration detected in both body and skin! "
                f"Drink {remaining} immediately. "
                f"Stop physical activity, rest in a cool place, "
                f"and apply moisturizer to your skin. "
                f"Seek medical attention if symptoms persist."
            )
        # Body Dehydrated
        elif body_status == "Dehydrated":
            remaining = f"{remaining_water_ml:.0f} ml" if remaining_water_ml else "water"
            return (
                f"🚨 Your body is severely dehydrated! "
                f"Drink {remaining} right now. "
                f"Avoid caffeine and alcohol. Rest immediately."
            )
        # Skin Dehydrated
        else:
            return (
                f"🚨 Your skin is severely dehydrated! "
                f"Drink water immediately and apply moisturizer. "
                f"Avoid sun exposure and stay in a humid environment."
            )