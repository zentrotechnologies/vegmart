
from .models import *
from rest_framework import serializers
from User.models import User,Role
class EmployeeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model= EmployeeMaster
        fields='__all__'
class CustomEmployeeMasterSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()
    def get_role_name(self, obj):
        obj_id = obj.role
        
        if obj_id is not None and obj_id !='' and obj_id !='None':
            try:
                obj = Role.objects.filter(id=obj_id).first()
                if obj is not None:
                   return obj.RoleName
                else:
                    return None
            except Role.DoesNotExist:
                return None
        return None
    class Meta:
        model= EmployeeMaster
        fields='__all__'