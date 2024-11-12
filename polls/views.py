from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Vote
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'polls/login.html'

    def get_success_url(self):
        next_url = self.request.GET.get('next')  # Get the next parameter from URL
        if next_url:
            return next_url  # Redirect to the page the user was trying to access
        return reverse_lazy('polls:index')  # Default to index if no 'next' parameter

    # Specify the correct template path

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        """Add voters list to context."""
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        # Get unique users who have voted for any choice in this question
        voters = User.objects.filter(vote__choice__question=question).distinct()
        context["voters"] = voters
        return context


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("polls:index"))
    else:
        form = SignUpForm()
    return render(request, "polls/signup.html", {"form": form})


@login_required
def vote(request, question_id):
    # Fetch the question or return a 404 error if it doesn't exist
    if not request.user.is_authenticated:
        return redirect(f'{reverse("polls:login")}?next={request.path}')

    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # If no choice was selected or it doesn't exist, redisplay the voting form with an error message
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        if request.method == 'POST':
            choice_id = request.POST.get('choice')
            choice = get_object_or_404(Choice, pk=choice_id)

            # Check if the user has already voted for any choice in this question
            if Vote.objects.filter(user=request.user, choice__question=question).exists():
                return redirect('polls:results', pk=question_id)

            # Record the vote
            Vote.objects.create(user=request.user, choice=choice)
            choice.votes = F('votes') + 1
            choice.save(update_fields=['votes'])

            return redirect('polls:results', pk=question_id)

        return redirect('polls:detail', pk=question_id)
