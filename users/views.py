from openai import AzureOpenAI
import requests
import openai
from .serializers import CourseRequestSerializer
from .models import CourseRequest
from .serializers import CourseSerializer, CourseRequestSerializer
from .models import Course, CourseRequest
from rest_framework import status
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
from .serializers import StudentSerializer, InstructorSerializer
# from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv
import os
from rest_framework.parsers import MultiPartParser, FormParser

# Load environment variables from .env file
load_dotenv()
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
    parser_classes = (MultiPartParser, FormParser)
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
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        course_requests = CourseRequest.objects.all()

        # Serialize each course request along with the related course data
        serialized_data = []
        for course_request in course_requests:
            serialized_course_request = CourseRequestSerializer(course_request).data
            # Include the related course data
            serialized_course_request['course'] = course_request.course.title
            serialized_data.append(serialized_course_request)
        return Response(serialized_data)

    def post(self, request):
        serializer = CourseRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Azure OpenAI API configuration
            azure_openai = AzureOpenAI(
               api_key=os.getenv('API_KEY'),
                api_version=os.getenv('API_VERSION'),
                azure_endpoint=os.getenv('AZURE_ENDPOINT')
            )

            course_instance = serializer.validated_data['course']
            course_data = CourseSerializer(course_instance).data
            prompt = f"Generate course content for student in K-12 from {course_data['title']}: {course_data['description']} : {course_data['outline']}"

            completion = azure_openai.chat.completions.create(
                model="Lerndise-gpt4",  # Specify the desired GPT model
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

            # Access the generated content from the completion and pass it to serializer
            generated_content = completion.choices[0].message.content
            print(generated_content)

            # Save the generated content to the course request
            course_request_instance = serializer.save(generated_content=generated_content)

            response_data = {
                'generated_content': generated_content,
                'course_title': course_data['title']
            }

            return Response({**serializer.data, **response_data}, status=status.HTTP_201_CREATED)
        """ This line merges the dictionaries serializer.data and response_data into a single dictionary and passes it as the first argument to Response, 
         and the status argument is specified separately. """

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
