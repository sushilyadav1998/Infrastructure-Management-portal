from rest_framework import serializers

from detail.models import serverinfo, File, basicinfo

class serverinfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = serverinfo
        fields = '__all__'

class basicinfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = basicinfo
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
