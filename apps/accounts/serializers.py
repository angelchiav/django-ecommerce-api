from rest_framework import serializers
from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed user profile serializer with all fields"""
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_email_verified',
            'is_phone_verified',
            'role',
            'date_of_birth',
            'profile_image',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
            'date_joined',
            'last_login',
        ]
        read_only_fields = [
            'id',
            'is_email_verified',
            'is_phone_verified',
            'role',
            'date_joined',
            'last_login',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'date_of_birth': {'required': False},
        }

    def validate_email(self, value):
        if not value.endswith("@gmail.com"):
            raise serializers.ValidationError("The email needs to be Gmail.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for public information"""
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'is_active',
            'date_joined',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer with password validation"""
    
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'phone',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "The passwords do not match."})
        
        # Validate password strength
        password_validation.validate_password(data['password'])
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.role = 'customer'  # Default role
        user.save()
        return user


class UserPasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("The current password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "The new passwords do not match."})
        
        validate_password(data['new_password'], self.context['request'].user)
        return data

# Reescritura del método save
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserAddressSerializer(serializers.ModelSerializer):
    """Serializer for user address information"""
    
    class Meta:
        model = User
        fields = [
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
        ]
