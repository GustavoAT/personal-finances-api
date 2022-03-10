from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def home(request):
    return Response(
        {'message': 'Personal finances API.'\
            f' Welcome {request.user.get_full_name()}'},
        status=status.HTTP_200_OK
    )