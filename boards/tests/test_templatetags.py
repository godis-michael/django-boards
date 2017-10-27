from django import forms
from django.test import TestCase

from ..templatetags.form_tags import field_type, input_class


class ExampleForm(forms.Form):
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        fields = ('name', 'password')


class FieldTypeTests(TestCase):
    def test_field_widget_type(self):
        form = ExampleForm()
        self.assertEquals(field_type(form['name']), 'TextInput')
        self.assertEquals(field_type(form['password']), 'PasswordInput')


class InputClassTests(TestCase):
    def test_unbound_form(self):
        form = ExampleForm()
        self.assertEquals(input_class(form['name']), 'form-control ')
        self.assertEquals(input_class(form['password']), 'form-control ')

    def test_bound_form_valid_data(self):
        data = {
            'name': 'john',
            'password': 'test123'
        }
        form = ExampleForm(data=data)
        self.assertEquals(input_class(form['name']), 'form-control is-valid')
        self.assertEquals(input_class(form['password']), 'form-control ')

    def test_bound_form_invalid_data(self):
        data = {
            'name': '',
            'password': 'test123'
        }
        form = ExampleForm(data=data)
        self.assertEquals(input_class(form['name']), 'form-control is-invalid')
        self.assertEquals(input_class(form['password']), 'form-control ')