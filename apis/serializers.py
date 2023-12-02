from rest_framework import serializers, viewsets
from .models import VDbApi, ClientPlans, Clients, UserTokens, Plans


class TokenSerializer(serializers.ModelSerializer):
    valid_till = serializers.DateTimeField(format="%Y %b %d")

    class Meta:
        model = UserTokens
        fields = ['user_token', 'valid_till']


class PlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plans
        fields = "__all__"


class ClientPlansSerializer(serializers.ModelSerializer):
    # plan_id = PlansSerializer(many=True)
    class Meta:
        model = ClientPlans
        fields = ['plan_id']


class ClientAllSerializer(serializers.ModelSerializer):
    user_tokens = TokenSerializer(many=True, read_only=True)
    client_plans = ClientPlansSerializer(many=True, read_only=True)

    class Meta:
        model = Clients
        fields = ['username', 'email', 'client_plans', 'user_tokens']


class VBADataSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = VDbApi
        fields = "__all__"


class VBAViewSets(viewsets.ModelViewSet):
    queryset = VDbApi.objects.all()[0:10]
    serializer_class = VBADataSerializer
