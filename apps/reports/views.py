from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import Warehouse, DailyReport, ExpenseCategory
from .serializers import (
    WarehouseSerializer, DailyReportSerializer, ExpenseCategorySerializer
)

class WarehouseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

class ExpenseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer

    def get_queryset(self):
        queryset = DailyReport.objects.all()
        start_date = self.request.query_params.get('startDate')
        end_date = self.request.query_params.get('endDate')
        warehouse_id = self.request.query_params.get('warehouse')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        
        return queryset.order_by('-date')

    @action(detail=False, methods=['post'])
    def sync(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'id': request.user.id
        })
