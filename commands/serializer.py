from rest_framework import serializers

from commands.models import responsecommand, filesystemdetails, mountpoint
'''
class executecommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = executecommand
        fields = '__all__'
'''
class responsecommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = responsecommand
        fields = '__all__'

class filesystemdetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = filesystemdetails
        fields = '__all__'

class mountpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = mountpoint
        fields = '__all__'
