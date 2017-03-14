from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Choice, Question
from django.template import loader
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone


# Create your views here.

#def index(request):
#    latest_question_list = Question.objects.order_by('-pub_date')[:5]
#    context = {
#        'latest_question_list':latest_question_list
#    }
#    return render(request,'polls/index.html',context)
#
#def detail(request,question_id):
#    question = get_object_or_404(Question,pk=question_id)
#    return render(request,'polls/detail.html',{'question':question})
#
#def results(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    return render(request, 'polls/results.html', {'question': question})

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    def get_queryset(self):
        """返回最近发布的五个投票（不包括那些被设置为在将来发布的）"""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
#
#    def get_queryset(self):
#        """返回最近发布的五个投票"""
#        return Question.objects.order_by('-pub_date')[:5]
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        过滤掉现在不应该被发布的投票。
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # 重新显示问题的投票表单
        return render(request, 'polls/detail.html', {
                      'question': p,
                      'error_message': "You didn't select a choice.",
                      })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # 成功处理之后 POST 数据之后，总是返回一个 HttpResponseRedirect 。防止因为用户点击了后退按钮而提交了两次。
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
