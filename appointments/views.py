from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class AppointmentListCreateView(APIView):
    def get(self, request):
        appointments = Appointment.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


