from rest_framework import generics, permissions
from .models import Appointment
from .serializers import AppointmentSerializer

# View for listing and creating appointments
class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    API view to list all appointments or create a new appointment.
    - Admins can see all appointments.
    - Clients can only see their own appointments.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    # Restrict access to authenticated users
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Admins can see all appointments; clients only see their own
        if self.request.user.is_staff: # Check for admin/staff
            return Appointment.objects.all()
        return Appointment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically set the user when creating an appointment
        serializer.save(user=self.request.user)
    
# View for retrieving, updating, and deleting a specific appointment
class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific appointment.
    - Admins can manage all appointments.
    - Clients can only manage their own appointments.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this appointment.")
        return obj