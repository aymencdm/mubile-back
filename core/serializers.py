from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, HydrationSession, WaterLog,
    BodyHydrationRecord, SkinHydrationRecord, FinalHydrationRecord
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'age', 'weight', 'height', 'gender']


class WaterLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterLog
        fields = ['id', 'amount', 'time']
        read_only_fields = ['time']


class HydrationSessionSerializer(serializers.ModelSerializer):
    logs = WaterLogSerializer(many=True, read_only=True)
    total_consumed_ml = serializers.SerializerMethodField()

    class Meta:
        model = HydrationSession
        fields = [
            'id', 'activity_level', 'weather', 
            'ambient_temperature', 'ambient_humidity',
            'start_time', 'end_time', 'total_consumed', 
            'total_consumed_ml', 'is_active', 'logs'
        ]
        read_only_fields = ['start_time', 'end_time', 'total_consumed']

    def get_total_consumed_ml(self, obj):
        """مجموع الماء المستهلك من كل الـ logs"""
        return sum(log.amount for log in obj.logs.all())


class BodyHydrationInputSerializer(serializers.Serializer):
    """
    Empty — البيانات تأتي من active session تلقائياً:
    - activity_level من session
    - weather من session  
    - water_consumed من WaterLogs
    """
    pass


class SkinHydrationInputSerializer(serializers.Serializer):
    """
    بيانات السوار فقط — Time_of_Day يُحسب تلقائياً
    """
    Electrical_Capacitance = serializers.FloatField()
    Skin_Temperature       = serializers.FloatField()
    Skin_Conductance       = serializers.FloatField()
    Ambient_Humidity       = serializers.FloatField()
    Ambient_Temperature    = serializers.FloatField()


class BodyHydrationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyHydrationRecord
        fields = [
            'id', 'physical_activity', 'water_consumed_today', 'weather',
            'recommended_water_goal_ml', 'remaining_water_ml',
            'predicted_hydration_level', 'hydration_percentage', 'created_at'
        ]
        read_only_fields = ['recommended_water_goal_ml', 'remaining_water_ml',
                            'predicted_hydration_level', 'hydration_percentage', 
                            'created_at']


class SkinHydrationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkinHydrationRecord
        fields = [
            'id', 'electrical_capacitance', 'skin_temperature', 'skin_conductance',
            'ambient_humidity', 'ambient_temperature', 'time_of_day',
            'predicted_hydration_level', 'hydration_percentage', 'created_at'
        ]
        read_only_fields = ['predicted_hydration_level', 'hydration_percentage', 
                            'created_at']


class FinalHydrationRecordSerializer(serializers.ModelSerializer):
    body_record = BodyHydrationRecordSerializer(read_only=True)
    skin_record = SkinHydrationRecordSerializer(read_only=True)

    class Meta:
        model = FinalHydrationRecord
        fields = [
            'id', 'body_record', 'skin_record', 'final_status', 
            'final_percentage', 'advice', 'created_at'
        ]
        read_only_fields = ['final_status', 'final_percentage', 'advice', 'created_at']