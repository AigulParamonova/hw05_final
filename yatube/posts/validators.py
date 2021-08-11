from django import forms


def validate_not_empty(text):
    if text == '':
        raise forms.ValidationError(
            'А кто поле будет заполнять, Пушкин?',
            params={'text': text},
        )
