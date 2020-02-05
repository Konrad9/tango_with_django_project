from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


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
    
    
class UserProfile(models.Model):
    # Required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to="profile_images", blank=True)
    
    def __str__(self):
        return self.user.username