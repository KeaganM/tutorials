from rest_framework import serializers
from .models import Article


# class ArticleSerializer(serializers.Serializer):
#     # need to add model fields
#     title = serializers.CharField(max_length=100)
#     author = serializers.CharField(max_length=100)
#     email = serializers.EmailField(max_length=100)
#     date = serializers.DateTimeField()
#
#     # have to write these because you are using serializer.Serializer
#     # don't have to if you use serializer.ModelSerializer
#     def create(self,validated_data):
#         return Article.objects.create(validated_data)
#
#     def update(self,instance,validated_data):
#         # need for all the model fields
#         instance.title = validated_data.get('title',instance.title)
#         instance.author = validated_data.get('title',instance.title)
#         instance.email = validated_data.get('title',instance.title)
#         instance.date = validated_data.get('title',instance.title)
#         instance.save
#         return instance

# model based serializer
# similar to above but it is all done for you
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        # these are the fields that will be serialized; essentially used could also do fields = "__all__"to get all fields
        fields = ["id","title","author"]


