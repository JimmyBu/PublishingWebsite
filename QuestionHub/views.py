# my_questions/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm


def question_list(request):
    questions = Question.objects.all()
    return HttpResponse(f"Questions: {', '.join(q.title for q in questions)}")


def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = Answer.objects.filter(question=question)
    return HttpResponse(f"Question: {question.title}, Answers: {', '.join(a.content for a in answers)}")


@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return HttpResponse(f"Question '{question.title}' asked successfully!")
    else:
        form = QuestionForm()
    return HttpResponse("Ask Question Form")
