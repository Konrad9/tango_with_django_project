from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page


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
    return render(request, "rango/about.html", context={"boldmessage":"This tutorial has been put together by me lol."})

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