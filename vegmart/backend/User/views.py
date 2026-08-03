from django.shortcuts import render

# Create your views here.from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,get_authorization_header)
from rest_framework import permissions
from rest_framework.response import Response
import json
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from .jwt import userJWTAuthentication
from django.template.loader import get_template, render_to_string
from django.core.mail import EmailMessage
from vegmart.settings import EMAIL_HOST_USER
from django.contrib.auth.hashers import make_password,check_password
from .common import CustomPagination
import re
import random
from django.core.mail import send_mail
from django.utils.timezone import make_aware
from django.utils import timezone
from django.db.models import F, FloatField, ExpressionWrapper,Q,Count
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt,Coalesce, TruncMonth,Cast

import math
from helpers.validations import hosturl
from helpers.custom_functions import *
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from Orders.models import *
from Orders.serializers import *

from Inventory.models import *
from Inventory.serializers import *


def createtoken(uuid,email,source):
    token = jwt.encode(
        {'id': uuid,
            'email': email,
            'source':source
           },
        settings.SECRET_KEY, algorithm='HS256')
    return token

class login(GenericAPIView):
    def post(self,request):
        email = request.data.get("email")
        Password = request.data.get("password")
        source = request.data.get("source")
        if email is None or Password is None :
            return Response( {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','email':'',"menuitems":[]},
                    "response":{
                    "status":"error",
                    'msg': 'Please provide email and password',
                    'n':0
                    }})
        
        userexist = User.objects.filter(email=email, isActive=True).first()
        if userexist is None:
           return Response(
                    {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','email':'',"menuitems":[]},
                    "response":{
                    "status":"error",
                    'msg': 'This user is not found',
                    'n':0
                    }}
                           )
        elif userexist.status == False:
            return Response(
                    {
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','email':'',"menuitems":[]},
                    "response":{
                    "status":"error",
                    'msg': 'This account is deactivated',
                    'n':0
                    }}
                           )
        else:
            p = check_password(Password,userexist.password)
            if p is False:
                return Response({
                    "data" : {'token':'','username':'','short_name':'','user_id':'','Menu':[],'role':'','role_name':'','email':'',"menuitems":[]},
                    "response":{
                    "status":"error",
                    'msg': 'Please enter correct password',
                    'n':0
                    }})
            else:
                useruuid = str(userexist.id)
                username = userexist.Username
                # short_name = ''.join([word[0] for word in username.split()]).upper()

                role =  userexist.role_id
                role_name =  str(userexist.role)
                ifservice_provider=False







                
                Token = createtoken(useruuid,email,source)
                
                if source == "Web":
                    web_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createwebtoken = UserToken.objects.create(User=useruuid,WebToken=Token,source=source)
                elif source == "Mobile":
                    mobile_tokenexist = UserToken.objects.filter(User=useruuid,isActive=True,source=source).update(isActive=False)
                    createmobiletoken = UserToken.objects.create(User=useruuid,MobileToken=Token,source=source)
                else:
                    return Response({
                        "data" : {'token':'','username':'','short_name':'','user_id':'','role':'','role_name':'','Menu':[],'email':'',"menuitems":[]},
                        "response":{
                        "status":"error",
                        'msg': 'Please Provide Source',
                        'n':0
                        }
                })

                # ================= GET MENU + PERMISSIONS =================
                rp_obj=RolePermissions.objects.filter(role=role,isActive=True)
                role_perms_menuids =list(rp_obj.filter(Q(add=True)|Q(view=True)|Q(edit=True)|Q(delete=True)).values_list('menu',flat=True))

                print("role_perms_menuids",role_perms_menuids)
                # permission_ser = PermissionsSerializer(permission_object,many=True)
                menus_objs = Menu.objects.filter(isActive=True, isshown=True,id__in=role_perms_menuids).order_by('id')

                menu_serializer=MenuSerializer(menus_objs,many=True)


                













                return Response({
                    "data" : {'token':Token,'username':username,'short_name':'','user_id':useruuid,'role':role,'role_name':role_name,'email':email,"menuitems":menu_serializer.data},
                    "response":{
                    "n": 1 ,
                    "msg" : "Login successful",
                    "status":"success"
                    }
                })
            
class logout(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
      
        auth_header = get_authorization_header(request)
        auth_data = auth_header.decode('utf-8')
        auth_token = auth_data.split(" ")
        token = auth_token[1]
        mobiletoken = UserToken.objects.filter(MobileToken=token,isActive=True).update(isActive=False)
        webtoken = UserToken.objects.filter(WebToken=token,isActive=True).update(isActive=False)
        return Response({
                        "data" : '',
                        "response":{
                        "n": 1 ,
                        "msg" : "Logout successful",
                        "status":"success"
                        }
                    })

class ChangePassword(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        id = request.user.id
        if id is not None:
            userObject = User.objects.filter(id=id,isActive=True,status=True).first()
        
            if userObject:
                password = request.data.get('oldpassword')
                currentPassword = check_password(password,userObject.password)
                if currentPassword==True:
                    newpassword = request.data.get('newpassword')
                
                    confirmpassword = request.data.get('confirmpassword')
                
                    if newpassword==confirmpassword:
                        data['password']= make_password(newpassword)
                        data['textPassword'] = newpassword
                        userSerializer = UserSerializer(userObject,data=data,partial=True)
                        if userSerializer.is_valid():
                            userSerializer.save()

                            tokenfalse = UserToken.objects.filter(User=id,isActive=True).update(isActive=False)
                           
                            return Response({"data":'',"response": {"n": 1, "msg": "Password updated successfully","status": "success"}})
                        else:
                            return Response({"data":'',"response": {"n": 0, "msg": "Password not updated ","status": "error"}})
                    else:
                        return Response({"data":'',"response": {"n": 0, "msg": "New and confirm password not matched ","status": "error"}})
                else:
                    return Response({"data":'',"response": {"n": 0, "msg": "Old password is wrong","status": "error"}})

        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Couldnt find id","status": "error"}})

class forgetpasswordmail(GenericAPIView):
    def post(self,request):
        data={}
        data['email']=request.data.get('email')
        userdata = User.objects.filter(email=data['email'],isActive=True,status=True).first()
        if userdata is not None:
            email =   data['email']
            data2 = {'user_id':userdata.id,'user_email':userdata.email,'frontend_url':hosturl}
            html_mail = render_to_string('mails/reset_password.html',data2)
            
            mailMsg = EmailMessage(
                'Forgot Password?',
                 html_mail,
                'no-reply@vegmart.com',
                [email],
                )
            mailMsg.content_subtype ="html"
            mailsend = mailMsg.send()
           
            return Response({"data":{},"response":{"n": 1,"msg":"Email Sent Successfully!", "status":"success" }})
        else:
            return Response({"data":{},"response":{"n": 0,"msg" : "User not found", "status":"error"}})



class setnewpassword(GenericAPIView):
    def post(self,request):
        data={}
        data['email']=request.data.get('email')
        empdata = User.objects.filter(email=data['email'],isActive=True,status=True).first()
        if empdata is not None:
            data['Password']=request.data.get('Password')
            data['cfpassword']=request.data.get('cfpassword')
            userpassword = data['Password']
            if data['Password'] != data['cfpassword']:
                return Response({"data":{},"response":{"n": 0 ,"msg":"Passwords do not match","status":"passwords do not match"}})
            else:
                data['password']=make_password(userpassword)
                data['textPassword'] = userpassword
                data['PasswordSet'] = True
                serializer = UserSerializer(empdata,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data" : serializer.data,"response":{"n":1,"msg":"Password set Successfully!","status":"success"}})
                else:

                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

        else:
            return Response({ "data":{},"response":{"n":0,"msg":"User not found", "status":"error"}})

class resetpassword(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        data['id']=request.data.get('id')
        empdata = User.objects.filter(id=data['id'],isActive=True,PasswordSet=True,status=True).first()
        if empdata is not None:
            data['Password']=request.data.get('Password')
            data['cfpassword']=request.data.get('cfpassword')
            userpassword = data['Password']
            if data['Password'] != data['cfpassword']:
                return Response({"data":{},"response":{"n": 0 ,"msg":"Passwords do not match","status":"passwords do not match"}})
            else:
                data['password']=make_password(userpassword)
                data['textPassword'] = userpassword
                serializer = UserSerializer(empdata,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"data" : serializer.data,"response":{"n":1,"msg":"Password Reset Successfully!","status":"success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

        else:
            return Response({ "data":{},"response":{"n":0,"msg":"User not found", "status":"error"}})
        
#role -----------------------------------------------------------------------------------------------------

class addrole(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['RoleName']=request.data.get('RoleName')
        result = []
        
        if data['RoleName'] is None or data['RoleName'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide Role name", "status":"error"}})
        
        
        # request_data['createdBy'] = request.session.get('user_id')
        if 'result' in request_data.keys():
            result = request_data['result']
        roleexist = Role.objects.filter(RoleName=data['RoleName'],isActive=True).first()
        if roleexist is None:
            serializer = Roleserializer(data=data)
            if serializer.is_valid():
                serializer.save()
                for i in result:
                    RolePermissions.objects.create(
                        role = serializer.data['id'],
                        add = i['create'],
                        view = i['read'],
                        edit = i['edit'],
                        delete = i['delete'],
                        menu= i['menu_id']
                    )
                return Response({"data" : serializer.data,"response":{"n":1,"msg":"Role added Successfully!","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({ "data":{},"response":{"n":0,"msg":"Role already exist", "status":"error"}})

class rolelist(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        role_objs = Role.objects.filter(isActive=True).order_by('id')
        serializer = Roleserializer(role_objs,many=True)
        return Response({
            "data" : serializer.data,
            "response":{
                "n":1,
                "msg":"Roles found Successfully",
                "status":"success"
                }
        })
    
class role_list_pagination_api(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def get(self,request):
        RoleMaster_objs = Role.objects.filter(isActive=True).order_by('id')
        page4 = self.paginate_queryset(RoleMaster_objs)
        serializer = Roleserializer(page4,many=True)
        return self.get_paginated_response(serializer.data)
    
class roleupdate(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('roleid')
        result = []
        if 'result' in request.data.keys():
            result = json.loads(request.data.get('result'))
        if id is not None and id !='':
            roleexist = Role.objects.filter(id=id,isActive= True).first()
            if roleexist is not None:
                data['RoleName']=request.data.get('RoleName')
                # data['updatedBy'] =str(request.user.id)
                if data['RoleName'] is None or data['RoleName'] =='':
                    return Response({ "data":{},"response":{"n":0,"msg":"Please provide Role name", "status":"error"}})
            
                roleindata = Role.objects.filter(RoleName=data['RoleName'],isActive= True).exclude(id=id).first()
                if roleindata is not None:
                    return Response({"data":'',"response": {"n": 0, "msg": "Role already exist","status": "error"}})
                else:
                    serializer = Roleserializer(roleexist,data=data,partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        RolePermissions.objects.filter(role=serializer.data['id']).delete()
                        for i in result:
                            RolePermissions.objects.create(
                                role = serializer.data['id'],
                                add = i['create'],
                                view = i['read'],
                                edit = i['edit'],
                                delete = i['delete'],
                                menu= i['menu_id']
                            )
                        return Response({"data":serializer.data,"response": {"n": 1, "msg": "Role updated successfully","status": "success"}})
                    else:
                        first_key, first_value = next(iter(serializer.errors.items()))
                        return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
            else:
                return Response({"data":'',"response": {"n": 0, "msg": "Role not found ","status": "error"}})
        else:
            data['RoleName']=request.data.get('RoleName')
            # data['updatedBy'] =str(request.user.id)
            if data['RoleName'] is None or data['RoleName'] =='':
                return Response({ "data":{},"response":{"n":0,"msg":"Please provide Role name", "status":"error"}})
            
            roleindata = Role.objects.filter(RoleName=data['RoleName'],isActive= True).first()
            if roleindata is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "Role already exist","status": "error"}})
            else:
                serializer = Roleserializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    for i in result:
                        RolePermissions.objects.create(
                            role = serializer.data['id'],
                            add = i['create'],
                            view = i['read'],
                            edit = i['edit'],
                            delete = i['delete'],
                            menu= i['menu_id']
                        )
                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "Role Added successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  

class rolebyid(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        id = request.data.get('roleid')
        roleobjects = Role.objects.filter(id=id,isActive=True).first()
        if roleobjects is not None:
            serializer = Roleserializer(roleobjects)
            permission_object = RolePermissions.objects.filter(role= id).order_by("menu")
            print("permission_object",permission_object.count())
            permission_ser = PermissionsSerializer(permission_object,many=True)

            serializer_data = serializer.data
            serializer_data.update({
                "permissions":permission_ser.data
            })
            return Response({"data":serializer_data,"response": {"n": 1, "msg": "Role data shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role data not found  ","status": "success"}})

class roledelete(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        id = request.data.get('roleid')
        existrole = Role.objects.filter(id=id,isActive=True).first()
        if existrole is not None:
            data['isActive'] = False
            serializer = Roleserializer(existrole,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "Role deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role Not Found","status": "error"}})

#user----------------------------------------------------------------------------------------------------

class createuser(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data={}
        request_data = request.data.copy()
        data['Username']=request.data.get('Username')
        if data['Username'] is None or data['Username'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user name", "status":"error"}})
        
        
        data['textPassword']=request.data.get('textPassword')
        if data['textPassword'] is None or data['textPassword'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user password", "status":"error"}})
        
        data['mobileNumber']=request.data.get('mobileNumber')
        if data['mobileNumber'] is None or data['mobileNumber'] =='':
            return Response({ "data":{},"response":{"n":0,"msg":"Please provide user mobile number", "status":"error"}})
        
        data['email']=request.data.get('email')
        data['role'] = request.data.get('role')
        data['password'] = data['textPassword']
        data['isActive'] = True
        result = []
        if 'result' in request.data.keys():
            result = request.data.get('result')

        roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
        if roleobj is not None:
            rolename = roleobj.RoleName
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "status": "error"}})

        emailobj = User.objects.filter(isActive=True, email=data['email']).first()
        mobileobj = User.objects.filter(isActive=True, mobileNumber=data['mobileNumber']).first()        
        if emailobj is not None:
            return Response({"data":'',"response": {"n": 0, "msg": "Email already exist", "status": "error"}})        
        elif mobileobj is not None:        
            return Response({"data":'',"response": {"n": 0, "msg": "Mobile already exist", "status": "error"}})
        
        else:
            serializer = UserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                userid = serializer.data['id']

                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User registered successfully","status":"success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        
class userlist(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        empobjects = User.objects.filter(isActive=True).order_by('id')
        serializer = CustomUserSerializer(empobjects, many=True)
        return Response({"data":serializer.data,"response": {"n": 1, "msg": "User list shown successfully","status": "success"}})

class user_list_pagination_api(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request):
        searchtext = request.data.get("searchtext")
        if searchtext is not None and searchtext != '':
            UserMaster_objs = User.objects.filter(Q(Username__icontains=searchtext,isActive=True)| Q(mobileNumber__icontains =searchtext,isActive=True)).order_by('Username')
        else:
            UserMaster_objs = User.objects.filter(isActive=True).order_by('Username')
        activation_status=request.data.get('activation_status')
        if activation_status is not None and activation_status !='':
            if activation_status == 'true':

                UserMaster_objs = UserMaster_objs.filter(status=True)
            elif activation_status == 'false':

                UserMaster_objs = UserMaster_objs.filter(status=False)     



        page4 = self.paginate_queryset(UserMaster_objs)
        serializer = CustomUserSerializer(page4,many=True)
        return self.get_paginated_response(serializer.data)

class userbyid(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        userID = request.data.get("userID")
        empobjects = User.objects.filter(id=userID,isActive=True).first()
        if empobjects is not None:
            serializer = UserSerializer(empobjects)
            serializer_data = serializer.data

            return Response({"data":serializer_data,"response": {"n": 1, "msg": "User shown successfully","status": "success"}})
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found  ","status": "success"}})
class userupdate(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userid = request.data.get('userid')
        data['userid'] = request.data.get('userid')
        existemp = User.objects.filter(id=userid,isActive=True).first()
        if existemp is not None:
            data['Username']=request.data.get('Username')
            data['mobileNumber']=request.data.get('mobileNumber')
            mobileNumber = data['mobileNumber']
            data['email']=request.data.get('email')
            email = data['email']
            data['role'] = request.data.get('role')
            data['isActive'] = True
            result = []
            if 'result' in request.data.keys():
                result = json.loads(request.data.get('result'))
            # data['updatedBy'] = str(request.user.id)

            roleobj = Role.objects.filter(id=data['role'],isActive=True).first()
            if roleobj is not None:
                rolename = roleobj.RoleName

            else:
                return Response({"data":'',"response": {"n": 0, "msg": "Role does not exist", "status": "error"}})
            serializer = UserSerializer(existemp,data=data,partial=True)
            emailObject = User.objects.filter(email__in = [email.strip().capitalize(),email.strip(),email.title()],isActive__in=[True]).exclude(id=userid).first()
            mobObject = User.objects.filter(mobileNumber = mobileNumber,isActive__in=[True]).exclude(id=userid).first()
            if emailObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this email id already exist","status": "error"}})
            elif mobObject is not None:
                return Response({"data":'',"response": {"n": 0, "msg": "User with this mobile number already exist","status": "error"}})
            else:
                if serializer.is_valid():
                    serializer.save()

                    return Response({"data":serializer.data,"response": {"n": 1, "msg": "User updated successfully","status": "success"}})
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})

class userdelete(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = request.data.get('userID')
        existemp = User.objects.filter(id=userID,isActive=True).first()
        if existemp is not None:
            data['isActive'] = False
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})

class delete_user_account(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = str(request.user.id)
        existemp = User.objects.filter(id=userID,isActive=True).first()
        if existemp is not None:

            data['isActive'] = False
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()

                if existemp.role_id == 1:
                    print("existemp.role_id",existemp.role_id)
                elif existemp.role_id == 2:
                    #delete service provider form service provider table
                    service_provider_obj=ServiceProvider.objects.filter(userid=userID,isActive=True).first()
                    if service_provider_obj is not None:
                        service_provider_obj.isActive=False
                        service_provider_obj.save()
                elif existemp.role_id == 3:
                    # delete customer form customer table
                    print("existemp.role_id",existemp.role_id)


                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User account deleted successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})


class userdeleteundo(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        userID = request.data.get('userID')
        existemp = User.objects.filter(id=userID,isActive=False).first()
        if existemp is not None:
            data['isActive'] = True
            serializer = UserSerializer(existemp,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"response": {"n": 1, "msg": "User retrived successfully","status": "success"}})
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                return Response({"data" : serializer.errors,"response":{"n":0,"msg":first_key+' : '+ first_value[0],"status":"error"}})  
        else:
            return Response({"data":'',"response": {"n": 0, "msg": "User not found ","status": "error"}})
      
#menu-----------------------------------------------------------------------------------------------
class Menulist(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        menuobj=Menu.objects.filter(isActive=True).order_by('id')
        serializer = MenuSerializer(menuobj,many=True)
        response_={
            'status':'success',
            'msg':'Menu List Found Successfully.',
            'data':serializer.data
        }
        return Response(response_,status=200)
       
class GetPermissionData(GenericAPIView):
    # authentication_classes=[userJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        data = {}
        data['role'] = request.data.get('role')
        roleobj = RolePermissions.objects.filter(role=data['role'], isActive=True).order_by('menu')
        if roleobj is not None:  
            serializer = PermissionsSerializer(roleobj,many=True)
            for i in serializer.data:
                menuobj=Menu.objects.filter(id=i['menu']).first()
                i['menu_path'] = menuobj.menuPath
                i['menu_name'] = menuobj.menuItem
                i['parent_id'] = menuobj.parentId
                i['sub_parent_id'] = menuobj.subparentId
            response_={
                    'status':'success',
                    'msg':'Permission found Successfully.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                'status':'error',
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)

class getmappingusers(GenericAPIView):
    authentication_classes=[userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        cclist = []
        # designlist = []
        # operationlist = []
        # budgetinglist = []
        # planninglist = []
        # Auditorlist = []

        ccuserobjs = User.objects.filter(isActive=True,role__in=Role.objects.filter(RoleName__iexact='GPL Users')).order_by('id')
        if ccuserobjs.exists():
            ccUserser = UserSerializer(ccuserobjs,many=True)

        
        auditobjs = User.objects.filter(isActive=True,role__in=Role.objects.filter(RoleName__iexact='Auditor')).order_by('id')
        if auditobjs.exists():
            auditUserser = UserSerializer(auditobjs,many=True)
            for a in auditUserser.data:
                cclist.append(a)

       


        context = {
            'cclist':cclist,
            # 'designlist':designlist,
            # 'operationlist':operationlist,
            # 'budgetinglist':budgetinglist,
            # 'planninglist':planninglist,
            # 'Auditorlist':Auditorlist
        }
         

        response_={
            'status':'success',
            'msg':'User list found  Successfully.',
            'data':context
        }
        return Response(response_,status=200)

    



# class admin_dashboard(GenericAPIView):
#     authentication_classes=[userJWTAuthentication]
#     permission_classes = (permissions.IsAuthenticated,)
#     def post(self,request):
#         month_total_order_value=0
#         month_total_order_value_diff=0
#         todays_total_sale_value=0
#         todays_total_sale_value_diff=0
#         inventory_value=0
#         pending_deliveries=0
#         monthly_sales_trend=[]
#         product_category_distribution=[]
#         recent_5_orders=[]
#         low_stocks=[]
#         todays_date=date.now()
#         current_month=date.now().month()
#         previous_month=date.now().month()
#         last_6_months=[]
#         inventory_base_query=Inventory.objects.filter(isActive=True,inventory_type="finished")
#         order_base_query=Order.objects.filter(isActive=True)
#         product_base_query=Product.objects.filter(isActive=True)


#         context={
#                 "month_total_order_value":month_total_order_value,
#                 "month_total_order_value_diff":month_total_order_value_diff,
#                 "todays_total_sale_value":todays_total_sale_value,
#                 "todays_total_sale_value_diff":todays_total_sale_value_diff,
#                 "inventory_value":inventory_value,
#                 "pending_deliveries":pending_deliveries,
#                 "monthly_sales_trend":monthly_sales_trend,
#                 "product_category_distribution":product_category_distribution,
#                 "recent_5_orders":recent_5_orders,
#                 "low_stocks":low_stocks,
#             }


        
#         return Response({"data":context,"response": {"n": 1, "msg": "User shown successfully","status": "success"}})

from datetime import timedelta
from decimal import Decimal

from django.db.models import (
    Sum,
    F,
    Value,
    DecimalField,
    ExpressionWrapper,
)
from django.utils import timezone
class admin_dashboard(GenericAPIView):
    authentication_classes = [userJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def calculate_percentage_difference(current_value, previous_value):
        current_value = Decimal(str(current_value or 0))
        previous_value = Decimal(str(previous_value or 0))

        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0

        difference = (
            (current_value - previous_value) / previous_value
        ) * Decimal("100")

        return round(float(difference), 2)

    @staticmethod
    def get_previous_month(month_start):
        previous_month_last_date = month_start - timedelta(days=1)
        return previous_month_last_date.replace(day=1)

    @staticmethod
    def get_last_six_months(current_month_start):
        months = []
        month_date = current_month_start

        for _ in range(6):
            months.append(month_date)
            previous_month_last_date = month_date - timedelta(days=1)
            month_date = previous_month_last_date.replace(day=1)

        return list(reversed(months))

    @staticmethod
    def safe_float(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError, InvalidOperation):
            return 0.0

    def post(self, request):
        try:
            today = timezone.localdate()
            tomorrow = today + timedelta(days=1)
            yesterday = today - timedelta(days=1)

            current_month_start = today.replace(day=1)
            previous_month_start = self.get_previous_month(current_month_start)

            inventory_base_query = Inventory.objects.filter(
                isActive=True,
                inventory_type="finished",
            )

            order_base_query = Order.objects.filter(isActive=True)

            # Products having at least one active variant.
            # ProductVariant.product is treated as a stored Product primary-key value.
            valid_product_ids = list(
                ProductVariant.objects.filter(isActive=True)
                .values_list("product", flat=True)
                .distinct()
            )
            print("valid_product_ids",valid_product_ids)
            product_base_query = Product.objects.filter(
                isActive=True,
                pk__in=valid_product_ids,
            )

            money_output = DecimalField(max_digits=18, decimal_places=2)
            zero_money = Value(
                Decimal("0.00"),
                output_field=money_output,
            )

            # 1. Current-month order value
            month_total_order_value = order_base_query.filter(
                createdAt__date__gte=current_month_start,
                createdAt__date__lt=tomorrow,
            ).aggregate(
                total=Coalesce(
                    Cast(Sum("total_amount"), money_output),
                    zero_money,
                )
            )["total"]

            # 2. Previous-month order value
            previous_month_total_order_value = order_base_query.filter(
                createdAt__date__gte=previous_month_start,
                createdAt__date__lt=current_month_start,
            ).aggregate(
                total=Coalesce(
                    Cast(Sum("total_amount"), money_output),
                    zero_money,
                )
            )["total"]

            month_total_order_value_diff = self.calculate_percentage_difference(
                month_total_order_value,
                previous_month_total_order_value,
            )

            # 3. Today's sales
            todays_total_sale_value = order_base_query.filter(
                createdAt__date=today,
            ).aggregate(
                total=Coalesce(
                    Cast(Sum("total_amount"), money_output),
                    zero_money,
                )
            )["total"]

            # 4. Yesterday's sales
            yesterdays_total_sale_value = order_base_query.filter(
                createdAt__date=yesterday,
            ).aggregate(
                total=Coalesce(
                    Cast(Sum("total_amount"), money_output),
                    zero_money,
                )
            )["total"]

            todays_total_sale_value_diff = self.calculate_percentage_difference(
                todays_total_sale_value,
                yesterdays_total_sale_value,
            )

            # 5. Inventory value: quantity × unit_cost.
            # unit_cost is currently a CharField, so it must be cast.
            inventory_value_expression = ExpressionWrapper(
                Cast(F("quantity"), money_output)
                * Cast(F("unit_cost"), money_output),
                output_field=money_output,
            )

            inventory_value = inventory_base_query.aggregate(
                total=Coalesce(
                    Sum(inventory_value_expression),
                    zero_money,
                )
            )["total"]

            # 6. Pending deliveries
            pending_deliveries = order_base_query.exclude(
                status__iexact="delivered"
            ).count()

            # 7. Monthly sales trend for last six months
            last_six_month_dates = self.get_last_six_months(
                current_month_start
            )
            sales_start_date = last_six_month_dates[0]

            monthly_sales_queryset = (
                order_base_query.filter(
                    createdAt__date__gte=sales_start_date,
                    createdAt__date__lt=tomorrow,
                )
                .annotate(month=TruncMonth("createdAt"))
                .values("month")
                .annotate(
                    total_sales=Coalesce(
                        Cast(Sum("total_amount"), money_output),
                        zero_money,
                    ),
                    total_orders=Count("pk"),
                )
                .order_by("month")
            )

            sales_by_month = {
                item["month"].date().replace(day=1): item
                for item in monthly_sales_queryset
                if item["month"]
            }

            monthly_sales_trend = []
            for month_date in last_six_month_dates:
                month_data = sales_by_month.get(month_date)

                monthly_sales_trend.append(
                    {
                        "month": month_date.strftime("%b %Y"),
                        "month_number": month_date.month,
                        "year": month_date.year,
                        "total_sales": self.safe_float(
                            month_data["total_sales"] if month_data else 0
                        ),
                        "total_orders": (
                            month_data["total_orders"] if month_data else 0
                        ),
                    }
                )

            # 8. Product category distribution
            # Product.category stores Category ID as plain text/integer, not FK.
            category_rows = list(
                product_base_query
                .exclude(category__isnull=True)
                .exclude(category__exact="")
                .values("category")
                .annotate(product_count=Count("pk"))
                .order_by("-product_count", "category")
            )

            category_ids = [
                row["category"]
                for row in category_rows
                if row["category"] not in (None, "")
            ]
            print("category_ids",category_ids)
            category_map = {
                str(category.pk): category.name
                for category in Category.objects.filter(
                    isActive=True,
                    pk__in=category_ids,
                )
            }

            grouped_product_count = sum(
                row["product_count"] or 0 for row in category_rows
            )

            product_category_distribution = []
            for row in category_rows:
                category_id = row["category"]
                product_count = row["product_count"] or 0

                product_category_distribution.append(
                    {
                        "category_id": category_id,
                        "category_name": category_map.get(
                            str(category_id),
                            str(category_id),
                        ),
                        "product_count": product_count,
                        "percentage": round(
                            (product_count / grouped_product_count) * 100,
                            2,
                        ) if grouped_product_count else 0,
                    }
                )

            # 9. Recent five orders
            recent_5_orders = [
                {
                    "order_id": order.pk,
                    "customer_id": order.customer_id,
                    "payment_mode": order.payment_mode,
                    "total_amount": self.safe_float(order.total_amount),
                    "taxable_amount": self.safe_float(order.taxable_amount),
                    "gst_amount": self.safe_float(order.gst_amount),
                    "paid_amount": self.safe_float(order.paid_amount),
                    "credit_amount": self.safe_float(order.credit_amount),
                    "due_date": order.due_date,
                    "status": order.status,
                    "created_at": order.createdAt,
                }
                for order in order_base_query.order_by("-createdAt")[:5]
            ]

            # 10. Low-stock finished inventory
            low_stock_queryset = list(
                inventory_base_query.filter(
                    Q(quantity__lte=0)
                    | Q(
                        minimum_stock__gt=0,
                        quantity__lte=F("minimum_stock"),
                    )
                ).order_by("quantity")[:10]
            )

            stock_ids = {
                str(inventory.stock_id)
                for inventory in low_stock_queryset
                if inventory.stock_id not in (None, "")
            }

            # Resolve stock_id robustly:
            # 1) direct Product primary key
            # 2) Product SKU
            # 3) ProductVariant primary key -> Product
            products_by_pk = {
                str(product.pk): product
                for product in Product.objects.filter(
                    isActive=True,
                    pk__in=[value for value in stock_ids if value.isdigit()],
                )
            }

            products_by_sku = {
                str(product.sku): product
                for product in Product.objects.filter(
                    isActive=True,
                    sku__in=stock_ids,
                )
            }

            variant_product_ids = {
                str(variant.pk): str(variant.product)
                for variant in ProductVariant.objects.filter(
                    isActive=True,
                    pk__in=[value for value in stock_ids if value.isdigit()],
                )
            }

            linked_product_ids = {
                product_id
                for product_id in variant_product_ids.values()
                if product_id
            }

            variant_products = {
                str(product.pk): product
                for product in Product.objects.filter(
                    isActive=True,
                    pk__in=linked_product_ids,
                )
            }

            low_stocks = []
            for inventory in low_stock_queryset:
                stock_id = str(inventory.stock_id)

                product = (
                    products_by_pk.get(stock_id)
                    or products_by_sku.get(stock_id)
                )

                if product is None:
                    linked_product_id = variant_product_ids.get(stock_id)
                    product = variant_products.get(str(linked_product_id))

                available_quantity = self.safe_float(inventory.quantity)
                minimum_stock = self.safe_float(inventory.minimum_stock)

                category_name = None
                if product and product.category not in (None, ""):
                    category_name = category_map.get(
                        str(product.category),
                        str(product.category),
                    )

                low_stocks.append(
                    {
                        "inventory_id": inventory.pk,
                        "stock_id": inventory.stock_id,
                        "product_id": product.pk if product else None,
                        "product_name": product.name if product else "Unknown Product",
                        "sku": product.sku if product else stock_id,
                        "category": category_name,
                        "sub_category": product.sub_category if product else None,
                        "brand": product.brand if product else None,
                        "warehouse": inventory.warehouse,
                        "batch": inventory.batch,
                        "inventory_type": inventory.inventory_type,
                        "available_quantity": available_quantity,
                        "minimum_stock": minimum_stock,
                        "unit": inventory.unit,
                        "unit_cost": inventory.unit_cost,
                        "stock_difference": round(
                            available_quantity - minimum_stock,
                            2,
                        ),
                        "stock_status": (
                            "out_of_stock"
                            if available_quantity <= 0
                            else "low_stock"
                        ),
                    }
                )

            context = {
                "month_total_order_value": self.safe_float(
                    month_total_order_value
                ),
                "previous_month_total_order_value": self.safe_float(
                    previous_month_total_order_value
                ),
                "month_total_order_value_diff": month_total_order_value_diff,
                "todays_total_sale_value": self.safe_float(
                    todays_total_sale_value
                ),
                "yesterdays_total_sale_value": self.safe_float(
                    yesterdays_total_sale_value
                ),
                "todays_total_sale_value_diff": todays_total_sale_value_diff,
                "inventory_value": self.safe_float(inventory_value),
                "pending_deliveries": pending_deliveries,
                "monthly_sales_trend": monthly_sales_trend,
                "product_category_distribution": product_category_distribution,
                "recent_5_orders": recent_5_orders,
                "low_stocks": low_stocks,
            }

            return Response(
                {
                    "data": context,
                    "response": {
                        "n": 1,
                        "msg": "Admin dashboard shown successfully",
                        "status": "success",
                    },
                },
            )

        except Exception as error:
            return Response(
                {
                    "data": {},
                    "response": {
                        "n": 0,
                        "msg": str(error),
                        "status": "error",
                    },
                },
            )


