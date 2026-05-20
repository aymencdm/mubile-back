from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    UserProfile, HydrationSession, WaterLog,
    BodyHydrationRecord, SkinHydrationRecord, FinalHydrationRecord
)
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    HydrationSessionSerializer, WaterLogSerializer,
    BodyHydrationInputSerializer, BodyHydrationRecordSerializer,
    SkinHydrationInputSerializer, SkinHydrationRecordSerializer,
    FinalHydrationRecordSerializer
)
from .utils import (
    calculate_water_goal, predict_hydration, predict_skin_hydration,
    calculate_body_percentage, body_status_from_percentage,
    calculate_final_percentage, final_hydration_status,
    temperature_to_weather, get_time_of_day, get_advice
)


def home(request):
    return HttpResponse("API is running 🚀")


# ═══════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Account created successfully"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def check_email(request):
    """Quick pre-check: is email/username already taken? (no auth required)"""
    from django.contrib.auth.models import User
    email    = request.data.get('email', '').strip().lower()
    username = request.data.get('username', '').strip()

    errors = {}
    if email and User.objects.filter(email__iexact=email).exists():
        errors['email'] = 'email_taken'
    if username and User.objects.filter(username__iexact=username).exists():
        errors['username'] = 'username_taken'

    if errors:
        return Response(errors, status=400)
    return Response({'ok': True})


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE
# ═══════════════════════════════════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return Response(UserProfileSerializer(profile).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Profile updated successfully"})
    return Response(serializer.errors, status=400)


# ═══════════════════════════════════════════════════════════════════════════
# HYDRATION SESSION
# ═══════════════════════════════════════════════════════════════════════════
# ✅ صح
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request):
    activity = request.data.get("activity_level")
    if not activity:
        return Response({"error": "activity_level is required"}, status=400)

    existing = HydrationSession.objects.filter(
        user=request.user, is_active=True
    ).first()
    if existing:
        total = sum(log.amount for log in existing.logs.all())
        existing.is_active = False
        existing.end_time = timezone.now()
        existing.total_consumed = total
        existing.save()

    ambient_temp = request.data.get("ambient_temperature")
    ambient_hum  = request.data.get("ambient_humidity")
    weather = temperature_to_weather(ambient_temp)

    session = HydrationSession.objects.create(
        user=request.user,
        activity_level=activity,
        weather=weather,
        ambient_temperature=ambient_temp,
        ambient_humidity=ambient_hum
    )

    return Response({
        "message": "Session started",
        "session_id": session.id,
        "weather": weather,
        "activity_level": activity
    }, status=201)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request):
    session = HydrationSession.objects.filter(user=request.user, is_active=True).first()
    if not session:
        return Response({"error": "No active session found"}, status=400)

    total = sum(log.amount for log in session.logs.all())
    session.is_active = False
    session.end_time = timezone.now()
    session.total_consumed = total
    session.save()

    return Response({"message": "Session ended", "total_consumed_ml": total})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_water(request):
    session = HydrationSession.objects.filter(user=request.user, is_active=True).first()
    if not session:
        return Response({"error": "No active session found"}, status=400)

    serializer = WaterLogSerializer(data=request.data)
    if serializer.is_valid():
        WaterLog.objects.create(session=session, amount=serializer.validated_data['amount'])
        total = sum(log.amount for log in session.logs.all())
        return Response({
            "message": "Water logged successfully",
            "total_consumed_ml": total
        }, status=201)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def undo_water(request):
    session = HydrationSession.objects.filter(user=request.user, is_active=True).first()
    if not session:
        return Response({"error": "No active session found"}, status=400)

    log_id = request.query_params.get('log_id')
    if log_id:
        log = session.logs.filter(id=log_id).first()
        if log:
            log.delete()
            total = sum(l.amount for l in session.logs.all())
            return Response({"message": "Water log deleted", "total_consumed_ml": total}, status=200)
        return Response({"error": "Log not found"}, status=404)

    last_log = session.logs.order_by('-time').first()
    if last_log:
        last_log.delete()
        total = sum(l.amount for l in session.logs.all())
        return Response({
            "message": "Last water log deleted",
            "total_consumed_ml": total
        }, status=200)
    
    return Response({"error": "No water logs to delete"}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_session(request):
    today = timezone.now().date()
    
    session = HydrationSession.objects.filter(
        user=request.user,
        is_active=True,
        start_time__date=today  # ✅ اليوم فقط
    ).first()
    
    if not session:
        return Response({"active_session": None}, status=200)
    
    return Response({
        "active_session": HydrationSessionSerializer(session).data
    }, status=200)
# ═══════════════════════════════════════════════════════════════════════════
# BODY AI
# ═══════════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_body_hydration(request):
    """
    Body analysis — يأخذ كل البيانات تلقائياً من session + profile.
    Flutter يرسل request فارغ: {}
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # 1️⃣ Validate profile
    if profile.age is None or profile.weight is None or profile.gender is None:
        return Response(
            {"error": "Please complete your profile first (age, weight, gender)"},
            status=400
        )

    # 2️⃣ Get active session
    session = HydrationSession.objects.filter(user=request.user, is_active=True).first()
    if not session:
        return Response(
            {"error": "No active session found. Please start a session first."},
            status=400
        )

    # 3️⃣ Pull data from session
    physical_activity = session.activity_level
    weather           = session.weather
    water_consumed    = sum(log.amount for log in session.logs.all())

    # 4️⃣ Calculate recommended goal
    recommended_goal = calculate_water_goal(
        weight=profile.weight,
        age=profile.age,
        gender=profile.gender,
        activity=physical_activity,
        weather=weather
    )

    # 5️⃣ Calculate Body Hydration % (water-based)
    body_percentage = calculate_body_percentage(water_consumed, recommended_goal)

    # 6️⃣ Get final label from percentage (not from AI model for body)
    predicted_level = body_status_from_percentage(body_percentage)

    # 7️⃣ Run AI for confidence score (reference only)
    _, body_confidence = predict_hydration(
        age=profile.age,
        weight=profile.weight,
        gender=profile.gender,
        activity=physical_activity,
        weather=weather,
        water_consumed_liters=water_consumed / 1000
    )

    remaining = max(recommended_goal - water_consumed, 0)

    # 8️⃣ Save record
    record = BodyHydrationRecord.objects.create(
        user=request.user,
        physical_activity=physical_activity,
        water_consumed_today=water_consumed,
        weather=weather,
        recommended_water_goal_ml=recommended_goal,
        remaining_water_ml=remaining,
        predicted_hydration_level=predicted_level,
        hydration_percentage=body_percentage
    )

    return Response({
        "record_id":                 record.id,
        "predicted_hydration_level": predicted_level,
        "hydration_percentage":      body_percentage,
        "ai_confidence":             body_confidence,
        "recommended_water_goal_ml": recommended_goal,
        "water_consumed_today_ml":   water_consumed,
        "remaining_water_ml":        remaining,
        "recommended_water_goal_ml": recommended_goal,
        "session_info": {
        "activity_level": physical_activity,
        "weather": weather
        }
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def body_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    latest = BodyHydrationRecord.objects.filter(user=request.user).first()
    return Response({
        "profile":       UserProfileSerializer(profile).data,
        "latest_record": BodyHydrationRecordSerializer(latest).data if latest else None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def body_history(request):
    records = BodyHydrationRecord.objects.filter(user=request.user).order_by('-created_at')[:30]
    return Response(BodyHydrationRecordSerializer(records, many=True).data)


# ═══════════════════════════════════════════════════════════════════════════
# SKIN AI
# ═══════════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_skin(request):
    """
    Skin analysis — Flutter يرسل بيانات السوار.
    Time_of_Day يُحسب تلقائياً.
    """
    serializer = SkinHydrationInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data

    # Auto Time_of_Day
    now = datetime.now()
    time_of_day = get_time_of_day()

    # AI prediction
    status, confidence, skin_percentage = predict_skin_hydration(
        electrical_capacitance = data['Electrical_Capacitance'],
        skin_temperature       = data['Skin_Temperature'],
        skin_conductance       = data['Skin_Conductance'],
        ambient_humidity       = data['Ambient_Humidity'],
        ambient_temperature    = data['Ambient_Temperature'],
        time_of_day            = time_of_day
    )

    record = SkinHydrationRecord.objects.create(
        user=request.user,
        electrical_capacitance = data['Electrical_Capacitance'],
        skin_temperature       = data['Skin_Temperature'],
        skin_conductance       = data['Skin_Conductance'],
        ambient_humidity       = data['Ambient_Humidity'],
        ambient_temperature    = data['Ambient_Temperature'],
        time_of_day            = time_of_day,
        predicted_hydration_level = status,
        hydration_percentage   = skin_percentage
    )

    return Response({
        "record_id":            record.id,
        "skin_status":          status,
        "hydration_percentage": skin_percentage,
        "ai_confidence":        confidence
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def skin_history(request):
    records = SkinHydrationRecord.objects.filter(user=request.user).order_by('-created_at')[:30]
    return Response(SkinHydrationRecordSerializer(records, many=True).data)


# ═══════════════════════════════════════════════════════════════════════════
# FINAL (Body + Skin Fusion)
# ═══════════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def final_status(request):
    """
    Fusion analysis — body من session + skin من request.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.age is None or profile.weight is None or profile.gender is None:
        return Response({"error": "Please complete your profile first"}, status=400)

    # ── Body: من session ──
    session = HydrationSession.objects.filter(user=request.user, is_active=True).first()
    if not session:
        return Response({"error": "No active session found"}, status=400)

    physical_activity = session.activity_level
    weather           = session.weather
    water_consumed    = sum(log.amount for log in session.logs.all())

    # ── Skin: من request ──
    skin_serializer = SkinHydrationInputSerializer(data=request.data)
    if not skin_serializer.is_valid():
        return Response(skin_serializer.errors, status=400)
    skin_data = skin_serializer.validated_data

    # Auto Time_of_Day
    now = datetime.now()
    time_of_day = round(now.hour + now.minute / 60.0, 2)

    # ── BODY prediction ──
    recommended_goal = calculate_water_goal(
        weight=profile.weight, age=profile.age, gender=profile.gender,
        activity=physical_activity, weather=weather
    )

    body_percentage = calculate_body_percentage(water_consumed, recommended_goal)
    body_status     = body_status_from_percentage(body_percentage)

    _, body_confidence = predict_hydration(
        age=profile.age, weight=profile.weight, gender=profile.gender,
        activity=physical_activity, weather=weather,
        water_consumed_liters=water_consumed / 1000
    )

    remaining = max(recommended_goal - water_consumed, 0)

    body_record = BodyHydrationRecord.objects.create(
        user=request.user,
        physical_activity=physical_activity,
        water_consumed_today=water_consumed,
        weather=weather,
        recommended_water_goal_ml=recommended_goal,
        remaining_water_ml=remaining,
        predicted_hydration_level=body_status,
        hydration_percentage=body_percentage
    )

    # ── SKIN prediction ──
    skin_status, skin_confidence, skin_percentage = predict_skin_hydration(
        electrical_capacitance = skin_data['Electrical_Capacitance'],
        skin_temperature       = skin_data['Skin_Temperature'],
        skin_conductance       = skin_data['Skin_Conductance'],
        ambient_humidity       = skin_data['Ambient_Humidity'],
        ambient_temperature    = skin_data['Ambient_Temperature'],
        time_of_day            = time_of_day
    )

    skin_record = SkinHydrationRecord.objects.create(
        user=request.user,
        electrical_capacitance    = skin_data['Electrical_Capacitance'],
        skin_temperature          = skin_data['Skin_Temperature'],
        skin_conductance          = skin_data['Skin_Conductance'],
        ambient_humidity          = skin_data['Ambient_Humidity'],
        ambient_temperature       = skin_data['Ambient_Temperature'],
        time_of_day               = time_of_day,
        predicted_hydration_level = skin_status,
        hydration_percentage      = skin_percentage
    )

    # ── FUSION ──
    final_result      = final_hydration_status(body_status, skin_status)
    final_pct         = calculate_final_percentage(body_percentage, skin_percentage)
    advice = get_advice(
    status=final_result,
    percentage=final_pct,
    body_status=body_status,
    skin_status=skin_status,
    remaining_water_ml=remaining,
    body_percentage=body_percentage,
    skin_percentage=skin_percentage,
    )

    final_record = FinalHydrationRecord.objects.create(
        user=request.user,
        body_record=body_record,
        skin_record=skin_record,
        final_status=final_result,
        final_percentage=final_pct,
        advice=advice
    )

    return Response({
        "final_record_id":      final_record.id,
        "body_status":          body_status,
        "body_percentage":      body_percentage,
        "body_confidence":      body_confidence,
        "skin_status":          skin_status,
        "skin_percentage":      skin_percentage,
        "skin_confidence":      skin_confidence,
        "final_status":         final_result,
        "final_percentage":     final_pct,
        "advice":               advice,
        "vibration":            final_result == "Dehydrated",
        "remaining_water_ml":   remaining,
        "recommended_water_goal_ml": recommended_goal,
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def final_history(request):
    records = FinalHydrationRecord.objects.filter(
        user=request.user
    ).order_by('-created_at')[:30] 
    return Response(FinalHydrationRecordSerializer(records, many=True).data)