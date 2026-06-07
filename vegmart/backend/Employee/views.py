from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from User.jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from User.common import CustomPagination
from django.db.models import Q
import math
from helpers.custom_functions import *
from User.models import *
from User.serializers import *



class addemployee(GenericAPIView):

    def post(self, request):

        data = {
            "employee_code": request.data.get("employee_code"),
            "first_name": request.data.get("first_name"),
            "last_name": request.data.get("last_name"),
            "full_name": request.data.get("full_name"),
            "email": request.data.get("email"),
            "mobile_number": request.data.get("mobile_number"),
            "alternate_mobile": request.data.get("alternate_mobile") or None,
            "designation": request.data.get("designation"),
            "department": request.data.get("department") or None,
            "role": request.data.get("role"),
            "joining_date": request.data.get("joining_date") or None,
            "relieving_date": request.data.get("relieving_date") or None,
            "reporting_manager": request.data.get("reporting_manager") or None,
            "gender": request.data.get("gender") or None,
            "date_of_birth": request.data.get("date_of_birth") or None,
            "address": request.data.get("address"),
            "city": request.data.get("city"),
            "state": request.data.get("state"),
            "pincode": request.data.get("pincode"),
            "status": request.data.get("status"),
            "user_id": None,
        }

        # Role Validation
        if not data.get('role'):

            return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Please select role",
                    "status": "error"
                }
            })

        roleobj = Role.objects.filter(
            id=data['role'],
            isActive=True
        ).first()

        if roleobj is None:

            return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Role does not exist",
                    "status": "error"
                }
            })

        # Date Conversion
        for field in ['joining_date', 'relieving_date', 'date_of_birth']:

            if data.get(field):

                try:
                    data[field] = datetime.strptime(
                        data[field],
                        '%d-%m-%Y'
                    ).strftime('%Y-%m-%d')

                except ValueError:
                    pass

        # Required Fields
        if not data["employee_code"]:
            return Response({
                "data": {},
                "response": {
                    "n": 0,
                    "msg": "Please provide employee code",
                    "status": "error"
                }
            })

        if not data["full_name"]:
            return Response({
                "data": {},
                "response": {
                    "n": 0,
                    "msg": "Please provide employee name",
                    "status": "error"
                }
            })

        # Employee Duplicate Checks
        if EmployeeMaster.objects.filter(
            employee_code=data["employee_code"],
            isActive=True
        ).exists():
            return Response({
                "data": {},
                "response": {
                    "n": 0,
                    "msg": "Employee code already exists",
                    "status": "error"
                }
            })

        if EmployeeMaster.objects.filter(
            email=data["email"],
            isActive=True
        ).exists():
            return Response({
                "data": {},
                "response": {
                    "n": 0,
                    "msg": "Email already exists",
                    "status": "error"
                }
            })

        if EmployeeMaster.objects.filter(
            mobile_number=data["mobile_number"],
            isActive=True
        ).exists():
            return Response({
                "data": {},
                "response": {
                    "n": 0,
                    "msg": "Mobile number already exists",
                    "status": "error"
                }
            })

        # User Duplicate Checks
        if User.objects.filter(
            mobileNumber=data["mobile_number"],
            isActive=True
        ).exists():
            return Response({
                "data": {},
                "response": {
                    "n": 0,
                    "msg": "User mobile number already exists",
                    "status": "error"
                }
            })

        if User.objects.filter(
            email=data["email"],
            isActive=True
        ).exists():
            return Response({
                "data": {},
                "response": {
                    "n": 0,
                    "msg": "User email already exists",
                    "status": "error"
                }
            })

        # Employee Serializer Validation
        serializer = EmployeeMasterSerializer(data=data)

        if not serializer.is_valid():

            first_key, first_value = next(
                iter(serializer.errors.items())
            )

            return Response({
                "data": serializer.errors,
                "response": {
                    "n": 0,
                    "msg": f"{first_key} : {first_value[0]}",
                    "status": "error"
                }
            })

        # Create User
        user_data = {
            "Username": data["full_name"],
            "mobileNumber": data["mobile_number"],
            "email": data["email"],
            "role_id": data["role"],
            "password": "12345",
            "isActive": True,
        }

        user_serializer = UserSerializer(data=user_data)

        if not user_serializer.is_valid():

            first_key, first_value = next(
                iter(user_serializer.errors.items())
            )

            return Response({
                "data": user_serializer.errors,
                "response": {
                    "n": 0,
                    "msg": f"{first_key} : {first_value[0]}",
                    "status": "error"
                }
            })

        user = user_serializer.save()

        employee = serializer.save(
            user_id=user.id
        )

        return Response({
            "data": EmployeeMasterSerializer(employee).data,
            "response": {
                "n": 1,
                "msg": "Employee registered successfully",
                "status": "success"
            }
        })
        
          
class employeelist(GenericAPIView):
    def get(self, request):

        objs = EmployeeMaster.objects.filter(
            isActive=True
        ).order_by("full_name")

        serializer = EmployeeMasterSerializer(
            objs,
            many=True
        )

        return Response({
            "data": serializer.data,
            "response": {
                "n": 1,
                "msg": "Employee list",
                "status": "success"
            }
        })

class employee_list_pagination_api(GenericAPIView):
    pagination_class = CustomPagination

    def post(self, request):

        objs = EmployeeMaster.objects.filter(
            isActive=True
        ).order_by("-id")

        search = request.data.get("search")

        if search:
            objs = objs.filter(
                Q(employee_code__icontains=search) |
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(mobile_number__icontains=search) |
                Q(department__icontains=search) |
                Q(designation__icontains=search)
            )

        page = self.paginate_queryset(objs)

        serializer = CustomEmployeeMasterSerializer(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)
    
class employeebyid(GenericAPIView):
    def post(self, request):

        employeeid = request.data.get("employeeid")

        obj = EmployeeMaster.objects.filter(
            id=employeeid,
            isActive=True
        ).first()

        if obj:
            serializer = EmployeeMasterSerializer(obj)

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Employee found",
                    "status": "success"
                }
            })

        return Response({
            "data": "",
            "response": {
                "n": 0,
                "msg": "Employee not found",
                "status": "error"
            }
        })
        
class employeeupdate(GenericAPIView):
    def post(self, request):
        data=request.data.copy()
        employeeid = request.data.get("employeeid")
        print("data",data)
        obj = EmployeeMaster.objects.filter(
            id=employeeid,
            isActive=True
        ).first()

        if not obj:
            return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Employee not found",
                    "status": "error"
                }
            })

        email = request.data.get("email")
        mobile_number = request.data.get("mobile_number")
        employee_code = request.data.get("employee_code")

        if EmployeeMaster.objects.filter(
            employee_code=employee_code,
            isActive=True
        ).exclude(id=employeeid).exists():
            return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Employee code already exists",
                    "status": "error"
                }
            })

        if EmployeeMaster.objects.filter(
            email=email,
            isActive=True
        ).exclude(id=employeeid).exists():
            return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Email already exists",
                    "status": "error"
                }
            })

        if EmployeeMaster.objects.filter(
            mobile_number=mobile_number,
            isActive=True
        ).exclude(id=employeeid).exists():
            return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Mobile number already exists",
                    "status": "error"
                }
            })
        if data.get('joining_date'):
            data['joining_date'] = datetime.strptime(
                data['joining_date'],
                '%d-%m-%Y'
            ).strftime('%Y-%m-%d')
        else:
            data['joining_date']=None
            
            
        if data.get('relieving_date'):
            data['relieving_date'] = datetime.strptime(
                data['relieving_date'],
                '%d-%m-%Y'
            ).strftime('%Y-%m-%d')
        else:
            data['relieving_date']=None
        if data.get('date_of_birth'):
            data['date_of_birth'] = datetime.strptime(
                data['date_of_birth'],
                '%d-%m-%Y'
            ).strftime('%Y-%m-%d')
        else:
            data['date_of_birth']=None
            
        user_obj = User.objects.filter(
            id=obj.user_id,
            isActive=True
        ).first()

        if user_obj:

            if User.objects.filter(
                email=email,
                isActive=True
            ).exclude(id=user_obj.id).exists():

                return Response({
                    "data": "",
                    "response": {
                        "n": 0,
                        "msg": "User email already exists",
                        "status": "error"
                    }
                })

            if User.objects.filter(
                mobileNumber=mobile_number,
                isActive=True
            ).exclude(id=user_obj.id).exists():

                return Response({
                    "data": "",
                    "response": {
                        "n": 0,
                        "msg": "User mobile number already exists",
                        "status": "error"
                    }
                })
        serializer = EmployeeMasterSerializer(
            obj,
            data=data,
            partial=True
        )




        if serializer.is_valid():

            employee = serializer.save()

            user_obj = User.objects.filter(
                id=employee.user_id,
                isActive=True
            ).first()

            if user_obj:

                user_obj.Username = employee.full_name
                user_obj.mobileNumber = employee.mobile_number
                user_obj.email = employee.email

                role_obj = Role.objects.filter(
                    id=employee.role,
                    isActive=True
                ).first()

                if role_obj:
                    user_obj.role_id = role_obj.id

                user_obj.save()

            return Response({
                "data": serializer.data,
                "response": {
                    "n": 1,
                    "msg": "Employee updated successfully",
                    "status": "success"
                }
            })
        first_key, first_value = next(iter(serializer.errors.items()))

        return Response({
            "data": serializer.errors,
            "response": {
                "n": 0,
                "msg": f"{first_key} : {first_value[0]}",
                "status": "error"
            }
        })
        
class employeedelete(GenericAPIView):
    def post(self, request):

        employeeid = request.data.get("employeeid")

        obj = EmployeeMaster.objects.filter(
            id=employeeid,
            isActive=True
        ).first()

        if not obj:
            return Response({
                "data": "",
                "response": {
                    "n": 0,
                    "msg": "Employee not found",
                    "status": "error"
                }
            })

        obj.isActive = False
        obj.status='TERMINATED'
        obj.save()

        return Response({
            "data": "",
            "response": {
                "n": 1,
                "msg": "Employee deleted successfully",
                "status": "success"
            }
        })
        
        
        
        
        