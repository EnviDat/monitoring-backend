from django.shortcuts import render


# Return 'lwf_documentation.html' with API documentation
def lwf_documentation(request):
    return render(request, 'lwf_documentation.html')
