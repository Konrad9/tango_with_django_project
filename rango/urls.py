from django.urls import path
from rango import views

app_name = "rango"

urlpatterns = [
        path("", views.IndexView.as_view(), name="index"),
        path("about/", views.AboutView.as_view(), name="about"),
        path("category/<slug:category_name_slug>/add_page/", 
             views.AddPageView.as_view(), name="add_page"),
        path("category/<slug:category_name_slug>/", 
             views.ShowCategoryView.as_view(), name = "show_category"),
        path("add_category/", views.AddCategoryView.as_view(), name="add_category"),
        path("register_profile/", views.RegisterProfileView.as_view(), name="register_profile"),
        #path("login/", views.user_login, name="login"),
        #path("logout/", views.user_logout, name="logout"),
        path("restricted/", views.restricted, name="restricted"),
        #path("search/", views.search, name="search"),
        path("goto/", views.goto_url, name="goto"),
        path("profiles/", views.ListProfilesView.as_view(), name="list_profiles"),
        path("profile/<username>/", views.ProfileView.as_view(), name="profile"),
    ]
