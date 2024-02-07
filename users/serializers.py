from rest_framework import serializers
from .models import User
from .models import User, Course, CourseRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']

    extra_kwargs = {
        'password': {'write_only': True}
    }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class StudentSerializer(UserSerializer):
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['role']

class InstructorSerializer(UserSerializer):
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['role']


class CourseSerializer(serializers.ModelSerializer):
    # generated_content = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description']
        # read_only_fields = ['instructor']

 

class CourseRequestSerializer(serializers.ModelSerializer):
    # course = serializers.CharField(source='course.title')
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    # generated_content = serializers.CharField(write_only=True, required=False)  # Mark as not required

    class Meta:
        model = CourseRequest
        fields = ['id', 'course', 'created_at', 'generated_content']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        generated_content = validated_data.pop('generated_content', '')  
        instance = super().create(validated_data)
        instance.generated_content = generated_content
        instance.save()
        return instance
    
    def get_generated_content(self, instance):
        return instance.generated_content
