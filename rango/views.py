from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserProfileForm, UserForm
from django.urls import reverse
#from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User


class AboutView(View):
    def get(self, request):
        context_dict = {}
        
        visitor_cookie_handler(request)
        context_dict["visits"] = request.session["visits"]
        context_dict["boldmessage"] = "This tutorial has been put together by Konrad."

        return render(request, "rango/about.html", context_dict)


class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, "rango/add_category.html", {"form":form})
    
    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save(commit = True)
            return redirect(reverse("rango:index"))
        else:
            print(form.errors)
            
        return render(request, "rango/add_category.html", {"form":form})
        
# responsible for main page view
class IndexView(View):
    def get(self, request):
        # Query the database for a list of ALL categories currently stored.
        # Order the categories by the number of likes in descending order.
        # Retrieve the top 5 only -- or all if less than 5.
        category_list = Category.objects.order_by("-likes")[:5]
        pages = Page.objects.order_by("-views")[:5]
        
        context_dict = {}
        context_dict["boldmessage"] = "Crunchy, creamy, cookie, candy, cupcake!"
        context_dict["pages"] = pages
        context_dict["categories"] = category_list
        
        # Increment counter
        visitor_cookie_handler(request)
        response = render(request, "rango/index.html", context=context_dict)
        
        return response
    

class ShowCategoryView(View):
    def populate_dictionary(self, category_name_slug):
        context_dict = {}
        try:
            # Can we find a category name slug with the given name?
            # If yes, then the .get() method returns one model instance.
            # If we cannot, the .get() method raises a DoesNotExist exception.
            category = Category.objects.get(slug = category_name_slug)
            
            # Retrive all of the associated pages.
            # The filter() will return a list of page objects or an empty list.
            pages = Page.objects.filter(category = category).order_by("-views")[:5]
            
            # Adds our results list to the template context under name pages.
            context_dict["pages"] = pages
            # We also add the category object from the database to the 
            # context dictionary. We will use this in the templage to verify
            # to verify that the category exists.
            context_dict["category"] = category
            
        except Category.DoesNotExist:
            # We get here if we didn't find the specified category. In this case,
            # the template will display the "no category" message.
            context_dict["category"] = None
            context_dict["pages"] = None
        
        return context_dict
    
    def get(self, request, category_name_slug):
        context_dict = self.populate_dictionary(category_name_slug)
        return render(request, "rango/category.html", context=context_dict)
    
    def post(self, request, category_name_slug):
        context_dict = self.populate_dictionary(category_name_slug)
        result_list = []
        query = ""
        if request.method == "POST":
            query = request.POST["query"].strip()
            if query:
                # Run the Bing search function to get the result list
                result_list = run_query(query)
        context_dict["result_list"] = result_list
        context_dict["query"] = query
        return render(request, "rango/category.html", context=context_dict)


class AddPageView(View):
    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        category = self.getCategory(category_name_slug)
        if category is None:
            return redirect(reverse("rango:index"))
        
        form = PageForm()
        context_dict = {"form":form, "category":category}
        return render(request, "rango/add_page.html", context=context_dict)
        
    
    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        category = self.getCategory(category_name_slug)
        if category is None:
            return redirect(reverse("rango:index"))
        
        form = PageForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()      
                return redirect(reverse("rango:show_category", kwargs={"category_name_slug":category_name_slug}))
        else:
            # The supplied form contained errors -
            # just print them to the terminal.
            print(form.errors)
            
        context_dict = {"form":form, "category":category}
        return render(request, "rango/add_page.html", context=context_dict)
        
    
    def getCategory(category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except:
            category = None
        return category


class RegisterProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        profile_form = UserProfileForm()
        return render(request, "rango/profile_registration.html", context = {"profile_form":profile_form})

    @method_decorator(login_required)
    def post(self, request):
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        # If the two forms are valid:
        if profile_form.is_valid(): 
            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False, which delays saving the model 
            # until we are ready to avoid integrity problems.
            profile = profile_form.save(commit = False)
            profile.user = request.user
            profile.save()
            
            return redirect(reverse("rango:index"))
        
        else:
            # Invalid form(s): print problems to terminal.
            print(profile_form.errors)
        return render(request, "rango/profile_registration.html", context = {"profile_form":profile_form})
    


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({"website":user_profile.website, 
                                "picture":user_profile.picture})
        return (user, user_profile, form)
    
    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse("rango:index"))
        
        context_dict = {"user_profile": user_profile, 
                        "selected_user": user,
                        "form": form}
        return render(request, "rango/profile.html", context_dict)
    
    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse("rango:index"))
        
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save(commit=True)
            return redirect("rango:profile", user.username)
        else:
            print(form.errors)
            
        context_dict = {"user_profile": user_profile,
                        "selected_user": user,
                        "form": form}
        return render(request, "rango/profile.html", context_dict)
    
    
class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()
        return render(request, "rango/list_profiles.html", {"user_profile_list":profiles})


class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET.get("category_id")
        
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)
        
        category.likes += 1
        category.save()
        
        return HttpResponse(category.likes)


class CategorySuggestionView(View):
    def get(self, request):
        if "suggestion" in request.GET:
            suggestion = request.GET.get("suggestion")
        else:
            suggestion = ""
            
        category_list=  get_category_list(max_results=8, starts_with=suggestion)
        
        if len(category_list)==0:
            category_list = Category.objects.order_by("-likes")
        
        return render(request, "rango/categories.html", {"categories":category_list})
    
    
class SearchAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        title = request.GET.get("title")
        url = request.GET.get("url")
        category_id = request.GET.get("category_id")
        
        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse("Error - category not found.")
        except ValueError:
            return HttpResponse("Error - bad category ID.")
        
        p = Page.objects.get_or_create(category = category, title = title, url = url)
        pages = Page.objects.filter(category = category).order_by("-views")
        return render(request, "rango/page_listing.html", {"pages": pages})
    
    
'''
def register(request):
    # A boolean telling the template whether the registration was succesful, 
    # set initially to false. Code changes it to true 
    # once the registration is complete.
    registered = False
    
    #If it is a HTTP post, we are interested in processing form data.
    if request.method == "POST":
        # Attempt to grap information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        # If the two forms are valid:
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            
            # Hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            
            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False, which delays saving the model 
            # until we are ready to avoid integrity problems.
            profile = profile_form.save(commit = False)
            profile.user = user
            
            # If the user provided a profile picture, we need to 
            # get it from the input form and put it in the UserProfile model.
            if "picture" in request.FILES:
                profile.picture = request.FILES["picture"]
                
            # Now save the UserProfile model instance.
            profile.save()
            
            # Update our variable to indicate that the template
            # registration was successful.
            registered = True
        
        else:
            # Invalid form(s): print problems to terminal.
            print(user_form.errors, profile_form.errors)
            
    else:
        # Not a HTTP post, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    # Render the template depending on the context.
    return render(request, "rango/register.html", context = {"user_form":user_form,
                                                             "profile_form":profile_form,
                                                             "registered":registered})
    
def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value does not exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return redirect(reverse('rango:index')) # reverse obtains the URL named index from views.py
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
        
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP get.
    else:
        # No context variables to pass to the template system, hence the 
        # blank dictionary object.
        return render(request, "rango/login.html")
    
    
# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse("rango:index"))
'''

@login_required
def restricted(request):
    return render(request, "rango/restricted.html")

#-----------------------------cookies-------------------------------------#

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie does not exists, the the default value of 1 is used.
    visits = int(get_server_side_cookie(request, "visits", "1"))
    
    last_visit_cookie = get_server_side_cookie(request, "last_visit", str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")
    
    # If it's been more than a day since the last visit,
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        # update the last visit cookie now that we have updated the count.
        request.session["last_visit"] = str(datetime.now())
    else:
        # set the last visit cookie.
        request.session["last_visit"] = last_visit_cookie
        
    # Update/set the visits cookie
    request.session["visits"] = visits
    
"""    
def search(request):
    result_list = []
    query=""
    
    if request.method == "POST":
        query = request.POST["query"].strip()
        if query:
            # Run the Bing search function to get the result list
            result_list = run_query(query)
            
    return render(request, "rango/search.html", {"result_list":result_list, "query":query})
"""

def goto_url(request):
    if request.method == "GET":
        page_id = request.GET.get("page_id")
        
        try:
            page = Page.objects.get(id = page_id)
        except Page.DoesNotExist:
            return redirect(reverse("rango:index"))
        
        page.views += 1
        page.save()
        return redirect(page.url)
    
    return redirect(reverse("rango:index"))
    
    
def get_category_list(max_results=0, starts_with=""):
    category_list = []
    
    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)
        
    if max_results>0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results]
            
    return category_list