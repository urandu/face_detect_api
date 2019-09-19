# The future is now!
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class Image(APIView):

    def post(self, request, *args, **kwargs):

            return Response({"you hit the view!!"}, status=status.HTTP_200_OK)
