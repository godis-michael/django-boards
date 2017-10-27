from django.core.urlresolvers import reverse


def create_response(client, url, data=None, pk=None):
    url = reverse(url, kwargs={'pk': pk}) if pk else reverse(url)
    response = client(url, data) if data else client(url)

    return response