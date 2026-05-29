from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Event, Booking
from .serializers import (
    CategorySerializer, EventListSerializer,
    EventDetailSerializer, BookingSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        # Anyone can READ, only admin can CREATE/UPDATE/DELETE
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(status='published').select_related('category')

    def get_permissions(self):
        # Anyone can READ, only admin can CREATE/UPDATE/DELETE
        if self.action in ['list', 'retrieve', 'upcoming', 'similar']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]

    def get_queryset(self):
        # Admin sees ALL events including drafts
        if self.request.user.is_staff:
            return Event.objects.all().select_related('category')
        return Event.objects.filter(status='published').select_related('category')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventListSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'city', 'status']
    search_fields = ['title', 'description', 'venue', 'tags']
    ordering_fields = ['date', 'price', 'rating']
    ordering = ['date']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        from django.utils import timezone
        upcoming = Event.objects.filter(
            status='published',
            date__gte=timezone.now().date()
        )[:10]
        serializer = EventListSerializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        event = self.get_object()
        similar = Event.objects.filter(
            category=event.category, status='published'
        ).exclude(id=event.id)[:4]
        serializer = EventListSerializer(similar, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related('event', 'event__category')

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'confirmed':
            booking.status = 'cancelled'
            booking.save()
            return Response({'message': 'Booking cancelled successfully.'})
        return Response(
            {'error': 'Cannot cancel this booking.'},
            status=status.HTTP_400_BAD_REQUEST
        )