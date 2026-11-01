from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from .models import (
    TransportLocation, TransportService,
    TransportReport, EmergencyHelpline
)

class TransportLocationSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district_slug = serializers.CharField(source='district.slug', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = TransportLocation
        fields = [
            'id', 'name', 'district', 'district_slug', 'district_name',
            'is_hub', 'phone', 'helpdesk_contact', 'latitude', 'longitude'
        ]


class TransportServiceSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()
    fare = serializers.SerializerMethodField()
    departureTime = serializers.CharField(source='departure_time', read_only=True)
    seats = serializers.CharField(source='total_seats', read_only=True)
    contacts = serializers.JSONField(source='contact_numbers', read_only=True)
    route = serializers.JSONField(source='route_stops', read_only=True)

    class Meta:
        model = TransportService
        fields = [
            'id', 'title', 'sub_title', 'service_type', 'badge_text', 'badge_color',
            'origin_name', 'destination_name', 'origin', 'destination', 'badge',
            'route_stops', 'route', 'departure_time', 'departureTime', 'estimated_fare',
            'fare', 'total_seats', 'seats', 'contact_phone', 'contact_numbers', 'contacts', 'image',
            'notes', 'status', 'verified', 'is_active', 'updated_at', 'created_at'
        ]
        read_only_fields = ['status', 'verified', 'is_active', 'created_at', 'updated_at']

    def get_image(self, obj):
        if obj.image:
            return make_absolute_url(obj.image, self.context.get('request'))
        return obj.image_url or "/images/yatayat/hero_bus.jpg"

    def get_origin(self, obj):
        return {
            'ne': getattr(obj, 'origin_name_ne', '') or obj.origin_name,
            'en': getattr(obj, 'origin_name_en', '') or obj.origin_name,
        }

    def get_destination(self, obj):
        return {
            'ne': getattr(obj, 'destination_name_ne', '') or obj.destination_name,
            'en': getattr(obj, 'destination_name_en', '') or obj.destination_name,
        }

    def get_badge(self, obj):
        return {
            'ne': getattr(obj, 'badge_text_ne', '') or obj.badge_text,
            'en': getattr(obj, 'badge_text_en', '') or obj.badge_text,
            'color': obj.badge_color,
        }

    def get_fare(self, obj):
        return {
            'ne': getattr(obj, 'estimated_fare_ne', '') or obj.estimated_fare,
            'en': getattr(obj, 'estimated_fare_en', '') or obj.estimated_fare,
        }

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            mapped = data.dict()
        elif hasattr(data, 'copy'):
            mapped = data.copy()
        else:
            mapped = dict(data)

        if 'service_name' in mapped and 'title' not in mapped:
            mapped['title'] = mapped['service_name']
        if 'vehicle_name' in mapped and 'title' not in mapped:
            mapped['title'] = mapped['vehicle_name']
        if 'vehicle_type' in mapped and 'service_type' not in mapped:
            mapped['service_type'] = mapped['vehicle_type']
        if 'origin' in mapped and 'origin_name' not in mapped:
            mapped['origin_name'] = mapped['origin']
        if 'route_from' in mapped and 'origin_name' not in mapped:
            mapped['origin_name'] = mapped['route_from']
        if 'destination' in mapped and 'destination_name' not in mapped:
            mapped['destination_name'] = mapped['destination']
        if 'route_to' in mapped and 'destination_name' not in mapped:
            mapped['destination_name'] = mapped['route_to']
        if 'route_waypoints' in mapped and 'route_stops' not in mapped:
            stops_val = mapped['route_waypoints']
            if isinstance(stops_val, str):
                mapped['route_stops'] = [s.strip() for s in stops_val.split(',') if s.strip()]
            else:
                mapped['route_stops'] = stops_val
        elif 'route_stops' in mapped and isinstance(mapped['route_stops'], str):
            mapped['route_stops'] = [s.strip() for s in mapped['route_stops'].split(',') if s.strip()]
        if 'fare' in mapped and 'estimated_fare' not in mapped:
            mapped['estimated_fare'] = mapped['fare']
        if 'phone' in mapped and 'contact_phone' not in mapped:
            mapped['contact_phone'] = mapped['phone']
        if 'contact_phone' in mapped and not mapped.get('contact_numbers'):
            mapped['contact_numbers'] = [mapped['contact_phone']]
        return super().to_internal_value(mapped)

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.FILES and 'image' in request.FILES:
            validated_data['image'] = request.FILES['image']
        return super().create(validated_data)


class TransportReportSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=TransportService.objects.all(), required=False, allow_null=True)

    class Meta:
        model = TransportReport
        fields = ['id', 'service', 'issue_type', 'description', 'reporter_phone', 'created_at']
        read_only_fields = ['created_at']

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            mapped = data.dict()
        elif hasattr(data, 'copy'):
            mapped = data.copy()
        else:
            mapped = dict(data)
        if 'issue_description' in mapped and 'description' not in mapped:
            mapped['description'] = mapped['issue_description']
        if 'report_type' in mapped and 'issue_type' not in mapped:
            mapped['issue_type'] = mapped['report_type']
        if 'service_name' in mapped and ('description' in mapped):
            if mapped.get('service_name'):
                mapped['description'] = f"[{mapped['service_name']}] {mapped['description']}"
        return super().to_internal_value(mapped)


class EmergencyHelplineSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = EmergencyHelpline
        fields = ['id', 'title', 'category', 'district', 'district_name', 'phone_number', 'subtitle', 'is_24_7', 'order']
