from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from .models import PopupAd
from .serializers import PopupAdSerializer

class PopupAdViewSet(viewsets.ModelViewSet):
    queryset = PopupAd.objects.all()
    serializer_class = PopupAdSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_ad = PopupAd.objects.filter(is_active=True).first()
        if not active_ad:
            return Response({"active": False, "data": None})
        serializer = self.get_serializer(active_ad, context={'request': request})
        return Response({"active": True, "data": serializer.data})
