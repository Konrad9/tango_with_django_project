from django.db import models
from django.template.defaultfilters import slugify

class Category(models.Model):
    MAX_LENGTH_NAME = 128
    name = models.CharField(max_length=MAX_LENGTH_NAME, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    MAX_LENGTH_TITLE = 128
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    MAX_LENGTH_URL = 200
    url = models.URLField(max_length=MAX_LENGTH_URL)
    views = models.IntegerField(default=0)


    def __str__(self):
        return self.title