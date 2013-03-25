# Api to Py

The purpose of API to Py(thon) is to be able to quickly access RESTful APIs
using Pythonic language constructs. It does so by converting attribute and item
accesses into URL parts to build endpoints (that represent URLs).

*Calls* to endpoints are then turned into actual HTTP requests.
The returned response is parsed as JSON data
into objects you can access either as dictionaries or using dot notation.

Example usage accessing the Sprint.ly API:

```python
from apitopy import Api

sprintly = Api('https://sprint.ly/api/', (USER, TOKEN),
                verify_ssl_cert=False, suffix='.json')
# initialise the API. Sprint.ly does not honor content negotiation,
# you must add the ".json" suffix to API requests

product = sprintly.products[9122]
# generates an endpoint https://sprint.ly/api/products/9122
# but doesn't perform any HTTP request yet

users = product.people()
# Issue an HTTP GET https://sprint.ly/api/products/9122/people.json
# Returns a list, result of the parsing of JSON data in the response

for user in users:
    # you can access user attributes as user['email'] or user.email
    print(u"#{id:<4} {first_name} {last_name} <{email}>".format(
        **user
    ))

items = product.items(assigned_to=2122, status='in-progress')
# HTTP GET https://sprint.ly/api/products/9122/items.json?assigned_to=2122&status=in-progress
# Returns a list of parsed JSON objects

for item in items:
    print(u"#{number:<4} {type:8} {status:12} {title:40}".format(
        **item
    ))
```
