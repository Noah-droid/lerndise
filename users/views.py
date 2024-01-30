from openai import AzureOpenAI
import requests
import openai
from .serializers import CourseRequestSerializer
from .models import CourseRequest
from .serializers import CourseSerializer, CourseRequestSerializer
from .models import Course, CourseRequest
from rest_framework import status
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
from .serializers import StudentSerializer, InstructorSerializer


class registerAPIView(APIView):
    def post(self, request):
        role = request.data.get('role', 'student')
        serializer_class = StudentSerializer if role == 'student' else InstructorSerializer
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found:)')

        if not user.check_password(password):
            raise AuthenticationFailed('Invalid password')

        payload = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt token': token
        }

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, 'secret', algorithms="HS256")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        user = User.objects.filter(id=payload['id']).first()
        if user.role == 'student':
            serializer = StudentSerializer(user)
        elif user.role == 'instructor':
            serializer = InstructorSerializer(user)
        else:
            serializer = UserSerializer(user)

        return Response(serializer.data)

        # cookies accessed if preserved


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'successful'
        }

        return response


class CourseListAPIView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseRequestAPIView(APIView):
    def post(self, request):
        serializer = CourseRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Azure OpenAI API configuration
            azure_openai = AzureOpenAI(
                api_key="b0704e3a203a4eac8a6bf7d934d87c55",
                api_version="2023-07-01-preview",
                azure_endpoint="https://lerndise-openai.openai.azure.com",

            )

            # Create a prompt for ChatGPT based on the course
            prompt = f"Generate course content for {serializer.validated_data['course']}"

            # Make a request to Azure OpenAI API
            completion = azure_openai.chat.completions.create(
                model="Lerndise-gpt4",  # Specify the desired GPT model
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            completion = completion.json()
            generated_content = completion['choices'][0]['message']['content']
            serializer.save(generated_content=generated_content)

            # Check if the request was successful
            # if completion.status_code == 200:

            #     return Response(serializer.data, status=status.HTTP_201_CREATED)
            # else:
            #     return Response({"error": "Failed to generate content"}, status=completion.status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
