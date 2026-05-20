from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import (
    home,
    register, check_email,
    get_profile, update_profile,
    start_session, end_session, log_water, undo_water, get_current_session,
    analyze_body_hydration, body_dashboard, body_history,
    analyze_skin, skin_history,
    final_status, final_history,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),

    path('api/token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/register/', register, name='register'),
    path('api/check-email/', check_email, name='check-email'),

    path('api/profile/', get_profile, name='profile-get'),
    path('api/profile/update/', update_profile, name='profile-update'),

    path('api/hydration/start/', start_session, name='session-start'),
    path('api/hydration/end/', end_session, name='session-end'),
    path('api/hydration/log/', log_water, name='session-log'),
    path('api/hydration/undo/', undo_water, name='session-undo'),
    path('api/hydration/current/', get_current_session, name='session-current'),

    path('api/body/analyze/', analyze_body_hydration, name='body-analyze'),
    path('api/body/dashboard/', body_dashboard, name='body-dashboard'),
    path('api/body/history/', body_history, name='body-history'),

    path('api/skin/analyze/', analyze_skin, name='skin-analyze'),
    path('api/skin/history/', skin_history, name='skin-history'),

    path('api/final/analyze/', final_status, name='final-analyze'),
    path('api/final/history/', final_history, name='final-history'),
]