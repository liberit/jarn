
from jarn.models import Document, Comment, Tag, MetaData
from django.contrib import admin


class DocAdmin(admin.ModelAdmin):
    list_display = ('title',)

class MetaAdmin(admin.ModelAdmin):
    list_display = ('key',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'document', 'text')


admin.site.register(Document, DocAdmin)
admin.site.register(MetaData, MetaAdmin)
admin.site.register(Comment , CommentAdmin)
admin.site.register(Tag     , TagAdmin)
