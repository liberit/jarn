
from django.db import models
from django.contrib.auth.models import User, Group


class MetaData(models.Model):
    key         = models.CharField(max_length=1023)
    value       = models.CharField(max_length=1023)


class Tag(models.Model):
    tag         = models.CharField(max_length=255)


class Document(models.Model):
    title       = models.CharField(max_length=1023)
    author      = models.ForeignKey(User)
    json        = models.TextField()
    added       = models.DateTimeField(auto_now=True)
    groups      = models.ManyToManyField(Group)
    tags        = models.ManyToManyField(Tag)
    metas       = models.ManyToManyField(MetaData)


class Comment(models.Model):
    text        = models.TextField()
    start       = models.CharField(max_length=1023)
    end         = models.CharField(max_length=1023)
    startOffset = models.IntegerField()
    endOffset   = models.IntegerField()
    length      = models.IntegerField()
    added       = models.DateTimeField(auto_now=True)
    document    = models.ForeignKey(Document)
    author      = models.ForeignKey(User)
    tags        = models.ManyToManyField(Tag)

