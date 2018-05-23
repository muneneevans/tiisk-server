from rest_framework import serializers

from django.conf.global_settings import EMAIL_HOST_USER

import requests, json


import members.models
import member_types.models
from .models import *


class UserInlineSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = "__all__"


class UserCreateSerializer(serializers.ModelSerializer):
    member_type = serializers.PrimaryKeyRelatedField(many=False, queryset=member_types.models.MemberType.objects.all(), write_only=True)
    email = serializers.EmailField(max_length=50, write_only=True)
    password = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = members.models.Member
        fields = '__all__'

    def create(self, validated_data):
        member_type = validated_data.pop('member_type')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        created_user = User.objects.create_user(email=email, password=password)
        member = members.models.Member(member_type=member_type, user=created_user, **validated_data)
        member.save()

        user_activation_token = ActivationToken.objects.create(
            user=created_user, token=get_random_string(length=6))
        user_activation_token.save()


        #send the token to the user
        subject, from_email, to = 'activation code', 'from@example.com', 'to@example.com'
        text_content = 'Welcome, the actication code for your account is %s' % (
            user_activation_token.token)
        html_content = '<p>The activation code is  <strong>%s</strong> message.</p>'%(user_activation_token.token)
        send_mail(subject,text_content,EMAIL_HOST_USER,[created_user.email],fail_silently=False)
        
        #register on mfs
        header = {"Authorization": "Bearer TestAPIKey"}
        payload = {
            "Request":{
                "mobile_number": member.phone_number,
                "customer_name": member.first_name + " " +created_user.last_name,
                "account_number": member.national_id,
                "customer_id_number": member.national_id,
                "registration_code": "7840",
                "email_address": created_user.email
            }
        }        


        r = requests.post("https://mobiloantest.mfs.co.ke/api/v1/whitelist/opt_in",
                  data=json.dumps(payload), headers=header)

        try:
            if(r.status_code == 200):
                response = r.json()
                if(response["Response"]['status_code'] == 200):
                    member.is_msf_active = True
                else:
                    member.is_msf_active = False
                member.save()
        except:
            # raise("cannot creat MFS account")
            pass

        return member


class CreateIndividualSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'national_id', 'phone_number',
                  'member_type', 'email', 'password')


class CreateBusinessSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('business_name', 'registration_number', 'business_email',
                  'business_phone_number', 'contact_name', 'contact_phone_number',
                  'contact_position', 'contact_email',
                  'member_type', 'email', 'password')


class CreateFutureSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = members.models.Member
        fields = ('member_type', 'email', 'password')