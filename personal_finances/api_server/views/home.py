from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def home(request):
    return Response(
        {'message': f'Personal finances API. Welcome {request.user.first_name}'},
        status=status.HTTP_200_OK
    )