from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from apps.districts.models import District
from apps.districts.serializers import DistrictSerializer
from .models import (
    Category, Author, Article, Tag, ArticleComment,
    BreakingNews, HomePagePlacement
)

User = get_user_model()

class CategorySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    parent_slug = serializers.SlugRelatedField(source='parent', slug_field='slug', read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(parent__isnull=True),
        source='parent', required=False, allow_null=True,
    )

    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'icon', 'image', 'parent_id', 'parent_slug', 'layout_type', 'order', 'show_in_menu']


class CategoryChildSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'icon', 'image', 'layout_type', 'order']


class CategoryMenuSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'icon', 'image', 'layout_type', 'order', 'parent', 'children']

    def get_children(self, obj):
        kids = getattr(obj, 'visible_children', None)
        if kids is None:
            kids = obj.children.filter(show_in_menu=True).order_by('order', 'id')
        return CategoryChildSerializer(kids, many=True, context=self.context).data

    def get_parent(self, obj):
        if not obj.parent_id:
            return None
        return CategoryChildSerializer(obj.parent, context=self.context).data


class AuthorSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'slug', 'name', 'bio', 'avatar', 'role', 'district']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ArticleSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    commentsCount = serializers.SerializerMethodField(read_only=True)
    og_image = serializers.SerializerMethodField(read_only=True)

    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True, required=False
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(), source='district', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featuredImage', 'imageCaption',
            'meta_title', 'meta_description', 'og_image',
            'author', 'category', 'district', 'tags', 'status', 'publishedAt', 'updatedAt', 'created_at',
            'featured', 'breaking', 'popular', 'readTime', 'views', 'likes', 'commentsCount',
            'author_id', 'category_id', 'district_id'
        ]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            if 'author' in data and not isinstance(data.get('author'), dict):
                data = data.copy()
                data['author_id'] = data.pop('author')
            if 'category' in data and not isinstance(data.get('category'), dict):
                data = data.copy()
                data['category_id'] = data.pop('category')
            if 'district' in data and not isinstance(data.get('district'), dict):
                data = data.copy()
                data['district_id'] = data.pop('district')
            if 'tags' in data and isinstance(data['tags'], list):
                self._incoming_tags = data['tags']
        return super().to_internal_value(data)

    def _save_tags(self, article):
        tags = getattr(self, '_incoming_tags', None)
        if tags is not None:
            Tag.objects.filter(article=article).delete()
            for t_name in tags:
                if t_name and str(t_name).strip():
                    Tag.objects.create(article=article, name=str(t_name).strip())

    def create(self, validated_data):
        article = super().create(validated_data)
        self._save_tags(article)
        return article

    def update(self, instance, validated_data):
        article = super().update(instance, validated_data)
        self._save_tags(article)
        return article

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags_list.all()]

    def get_commentsCount(self, obj):
        return obj.comments.count()

    def get_og_image(self, obj):
        return make_absolute_url(obj.featuredImage, self.context.get('request'))


class ArticleCommentSerializer(serializers.ModelSerializer):
    replyCount = serializers.SerializerMethodField()

    class Meta:
        model = ArticleComment
        fields = '__all__'
        read_only_fields = ['user']
        extra_kwargs = {
            'article': {'required': False},
            'parent': {'required': False, 'allow_null': True}
        }

    def get_replyCount(self, obj):
        return obj.replies.count()

    def validate(self, attrs):
        if 'article' not in attrs:
            val = self.initial_data.get('article') or self.initial_data.get('articleId')
            if val:
                if str(val).isdigit():
                    article = Article.objects.filter(id=int(val)).first()
                else:
                    article = Article.objects.filter(slug=str(val)).first()
                if article:
                    attrs['article'] = article
                else:
                    raise serializers.ValidationError({'article': f'Article "{val}" not found.'})
            else:
                raise serializers.ValidationError({'article': 'Article is required.'})

        parent_val = self.initial_data.get('parent') or self.initial_data.get('parentId')
        if parent_val:
            parent_obj = ArticleComment.objects.filter(id=int(parent_val)).first()
            if parent_obj:
                attrs['parent'] = parent_obj

        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['articleId'] = str(instance.article_id)
        ret['parentId'] = str(instance.parent_id) if instance.parent_id else None
        return ret


class BreakingNewsSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BreakingNews
        fields = ['id', 'text', 'href', 'publishedAt']


class HomePagePlacementSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = HomePagePlacement
        fields = ['id', 'section_name', 'articles']
