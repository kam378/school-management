from myapps.accounts.models import User
from django.db.models import Count

class QuotaManager:
    @staticmethod
    def can_add_student(tenant):
        if not tenant.subscription_plan:
            return True  # Or False, depending on default policy. Let's say True for now.
        
        current_count = User.objects.filter(role='student').count()
        return current_count < tenant.subscription_plan.max_students

    @staticmethod
    def can_add_teacher(tenant):
        if not tenant.subscription_plan:
            return True
            
        current_count = User.objects.filter(role='teacher').count()
        return current_count < tenant.subscription_plan.max_teachers

    @staticmethod
    def get_usage_stats(tenant):
        if not tenant.subscription_plan:
            return None
            
        stats = {
            'students': User.objects.filter(role='student').count(),
            'max_students': tenant.subscription_plan.max_students,
            'teachers': User.objects.filter(role='teacher').count(),
            'max_teachers': tenant.subscription_plan.max_teachers,
        }
        
        stats['student_percent'] = (stats['students'] / stats['max_students'] * 100) if stats['max_students'] > 0 else 0
        stats['teacher_percent'] = (stats['teachers'] / stats['max_teachers'] * 100) if stats['max_teachers'] > 0 else 0
        
        return stats
