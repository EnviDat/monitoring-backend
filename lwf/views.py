from django.shortcuts import render


# Return 'lwf_documentation.html' with API documentation
def lwf_documentation(request, parent_class):
    context = {'parameters':
                   {'test_key': {'param': 'test_value', 'long_name': 'test_value1', 'units': 'm/s'},
                    'test_key2': {'param': 'test_value2param', 'long_name': 'test_value2', 'units': 'mph'}
                    }
               }
    return render(request, 'lwf_documentation.html', context)
