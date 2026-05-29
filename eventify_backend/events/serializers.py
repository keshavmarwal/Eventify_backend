from rest_framework import serializers
from .models import Category, Event, Booking


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon')


class EventListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'slug', 'category', 'category_name',
            'venue', 'city', 'date', 'time',
            'price', 'available_seats', 'total_seats',
            'rating', 'badge', 'tags', 'status',
        )


class EventDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    available_seats = serializers.IntegerField(read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'slug', 'description',
            'category', 'category_id',
            'venue', 'city', 'address',
            'date', 'time', 'price',
            'total_seats', 'available_seats', 'is_sold_out',
            'tags', 'badge', 'status', 'rating',
            'created_at', 'updated_at',
        )


class BookingSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateField(source='event.date', read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'event', 'event_title', 'event_date',
            'quantity', 'total_price', 'status', 'reference', 'booked_at'
        )
        read_only_fields = ('total_price', 'status', 'reference', 'booked_at')

    def validate(self, data):
        event = data['event']
        quantity = data.get('quantity', 1)
        if event.available_seats < quantity:
            raise serializers.ValidationError(
                f"Only {event.available_seats} seats available."
            )
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)