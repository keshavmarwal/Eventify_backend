from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, EventViewSet, BookingViewSet
 
# 📘 LEARN: DRF Router automatically generates URL patterns for ViewSets
# One router.register() creates ALL of these:
#   GET    /events/          → list
#   POST   /events/          → create
#   GET    /events/{id}/     → retrieve
#   PUT    /events/{id}/     → update
#   PATCH  /events/{id}/     → partial_update
#   DELETE /events/{id}/     → destroy
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
 
urlpatterns = [
    path('', include(router.urls)),
]