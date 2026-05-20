from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.PositiveIntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.user.username


class HydrationSession(models.Model):
    ACTIVITY_CHOICES = [("Low", "Low"), ("Moderate", "Moderate"), ("High", "High")]
    WEATHER_CHOICES  = [("Cold", "Cold"), ("Normal", "Normal"), ("Hot", "Hot")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hydration_sessions")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, default="Normal")
    ambient_temperature = models.FloatField(null=True, blank=True)  # snapshot من sensor
    ambient_humidity = models.FloatField(null=True, blank=True)     # snapshot من sensor
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_consumed = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_level} - {self.weather}"


class WaterLog(models.Model):
    session = models.ForeignKey(HydrationSession, on_delete=models.CASCADE, related_name="logs")
    amount = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} ml"


class BodyHydrationRecord(models.Model):
    ACTIVITY_CHOICES = [("Low", "Low"), ("Moderate", "Moderate"), ("High", "High")]
    WEATHER_CHOICES  = [("Cold", "Cold"), ("Normal", "Normal"), ("Hot", "Hot")]
    HYDRATION_CHOICES = [("Hydrated", "Hydrated"), ("Warning", "Warning"), ("Dehydrated", "Dehydrated")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="body_hydration_records")
    physical_activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    water_consumed_today = models.FloatField()
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES)
    recommended_water_goal_ml = models.FloatField()
    remaining_water_ml = models.FloatField()
    predicted_hydration_level = models.CharField(max_length=20, choices=HYDRATION_CHOICES)
    hydration_percentage = models.FloatField(default=0)  # ← جديد
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.predicted_hydration_level} - {self.created_at.date()}"


class SkinHydrationRecord(models.Model):
    HYDRATION_CHOICES = [("Hydrated", "Hydrated"), ("Dehydrated", "Dehydrated")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skin_hydration_records")
    electrical_capacitance = models.FloatField(null=True, blank=True)
    skin_temperature       = models.FloatField(null=True, blank=True)
    skin_conductance       = models.FloatField(null=True, blank=True)
    ambient_humidity       = models.FloatField(null=True, blank=True)
    ambient_temperature    = models.FloatField(null=True, blank=True)
    time_of_day            = models.FloatField(null=True, blank=True)
    predicted_hydration_level = models.CharField(max_length=20, choices=HYDRATION_CHOICES)
    hydration_percentage = models.FloatField(default=0)  # ← جديد
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.predicted_hydration_level} - {self.created_at.date()}"


class FinalHydrationRecord(models.Model):
    HYDRATION_CHOICES = [("Hydrated", "Hydrated"), ("Warning", "Warning"), ("Dehydrated", "Dehydrated")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="final_hydration_records")
    body_record = models.ForeignKey(BodyHydrationRecord, on_delete=models.CASCADE, related_name="final_results")
    skin_record = models.ForeignKey(SkinHydrationRecord, on_delete=models.CASCADE, related_name="final_results")
    final_status = models.CharField(max_length=20, choices=HYDRATION_CHOICES)
    final_percentage = models.FloatField(default=0)  # ← جديد
    advice = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.final_status} - {self.created_at.date()}"