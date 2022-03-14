from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    # validated_data is from the POST payload
    def create(self, validated_data):
        """Create a new user, with encrypted password, and return it"""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        # this is True by deafult, we change it
        trim_whitespace=False
    )

    # validate, using Django REST Framework serializers as a base
    def validate(self, attrs):
        """Validate and authenticate the user"""
        user = authenticate(
            # context attribute is passed by
            # the Serializer class in Django Rest Framework
            request=self.context.get('request'),
            email=attrs.get('email'),
            password=attrs.get('password')
        )
        if not user:
            msg = ugettext_lazy(
                'Unable to authenticate with provided credentials'
            )
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        # usually (or always?) the attrs should be returned
        return attrs
