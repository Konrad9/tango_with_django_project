from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserProfileForm, UserForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# responsible for main page view
def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    category_list = Category.objects.order_by("-likes")[:5]
    pages = Page.objects.order_by("-views")[:5]
    
    # Construct a dictionary to pass to the template engine as its context.
    # Place the list in our context_dict dictionary (with our boldmessage!)
    # that will be passed to the template engine.
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    context_dict = {}
    context_dict["boldmessage"] = "Crunchy, creamy, cookie, candy, cupcake!"
    context_dict["pages"] = pages
    context_dict["categories"] = category_list
    
    
    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, "rango/index.html", context=context_dict)

    
def about(request):
    return render(request, "rango/about.html", context={"boldmessage":"This tutorial has been put together by Konrad."})

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rndering engine
    context_dict = {}
    
    try:
        # Can we find a category name slug with the given name?
        # If yes, then the .get() method returns one model instance.
        # If we cannot, the .get() method raises a DoesNotExist exception.
        category = Category.objects.get(slug = category_name_slug)
        
        # Retrive all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category = category)#.order_by("-views")[:5]
        
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
        
    # Render the response and return it ot the client
    return render(request, "rango/category.html", context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    
    # A HTTP post?
    if request.method == "POST":
        form = CategoryForm(request.POST)
        
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit = True)
            # Now that the category is saved, we could confirm this.
            # For now, just redirect the user back to the index view.
            return redirect("/rango/")
        else:
            # The supplied form contained errors -
            # just print them to the terminal.
            print(form.errors)
            
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the frm with error messages (if any).
    return render(request, "rango/add_category.html", {"form":form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
        
    if category is None:
        return redirect("/rango/")
        
    form = PageForm()
    
    # A HTTP post?
    if request.method == "POST":
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

@login_required
def restricted(request):
    return render(request, "rango/restricted.html")