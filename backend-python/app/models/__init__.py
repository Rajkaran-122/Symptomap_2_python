"""Initialize models package"""

from app.models.user import User
from app.models.chatbot import ChatbotConversation, AnonymousSymptomReport, DiseaseInfo
from app.models.outbreak import Hospital, Outbreak, Prediction, Alert
from app.models.doctor import DoctorOutbreak, DoctorAlert
from app.models.broadcast import Broadcast
from app.models.notification_preference import NotificationPreference

__all__ = [
    "User", 
    "ChatbotConversation", 
    "AnonymousSymptomReport", 
    "DiseaseInfo",
    "Hospital",
    "Outbreak", 
    "Prediction", 
    "Alert",
    "DoctorOutbreak",
    "DoctorAlert",
    "Broadcast",
    "NotificationPreference"
]


