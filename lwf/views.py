from django.shortcuts import render


# Return 'lwf_documentation.html' with API documentation
def lwf_documentation(request, parent_class):
    context = {'object':
                   {'test_key': 'test_value',
                    'test_key2': 'test_value2'}
               }
    return render(request, 'lwf_documentation.html', context)
