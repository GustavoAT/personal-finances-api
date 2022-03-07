from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def delete_token(request):
    delete_result = Token.objects.filter(user=request.user).delete()
    return Response(
        {'deleted': delete_result[0]},
        status=status.HTTP_200_OK
    )