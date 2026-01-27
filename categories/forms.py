from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-500 rounded-md shadow-sm bg-gray-300 text-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-300 text-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            }),
            'color': forms.ColorInput(attrs={
                'class': 'w-10 h-10 border border-gray-300 bg-gray-300 text-gray-800 rounded cursor-pointer'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        # If user is provided, ensure the form is associated with the user
        if user:
            self.user = user

    def clean_name(self):
        name = self.cleaned_data.get('name')
        category_type = self.cleaned_data.get('type')

        # Check for uniqueness: name must be unique per user and type
        if hasattr(self, 'user'):
            if Category.objects.filter(
                user=self.user,
                name=name,
                type=category_type
            ).exists():
                raise forms.ValidationError(f'A category with the name "{name}" already exists for this type.')

        return name
