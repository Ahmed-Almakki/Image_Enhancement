import json


class RequestMiddlewate:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.content_type == 'application/json':
            print('-'*40, f'\ninside the middleware')
            try:
                # Django request class have these attribute
                # request.body - .META  - .POST  - .GET
                data = json.loads(request.body.decode('utf-8'))
            except Exception as e:
                print(f"custome middleware error: {e}")

            # better to return new object for the body and call it new name like new_body
            request.new_body = data

        response = self.get_response(request)
        print('return the response')
        return response

