from django.test import TestCase
from ..forms import MyUserChangeForm

class FormsTests(TestCase):
    def test_myuserchangeform_has_correct_fields(self):
        form = MyUserChangeForm()
        num_of_fields = len(form.fields)
        field_names = list(form.fields.keys())
        self.assertEqual(num_of_fields, 3)
        self.assertListEqual(field_names, ["first_name", "last_name", "email"])