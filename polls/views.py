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
    question = get_object_or_404(Question, pk=question_id)

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
