from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import CreateAccountForm


class CreateAccountView(FormView):
    template_name = "bookmaze/form_view.html"
    form_class = CreateAccountForm
    success_url = reverse_lazy("maze:index")

    def form_valid(self, form):
        form.create_user(self.request)
        return super().form_valid(form)
