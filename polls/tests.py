import datetime
from django.utils import timezone
from django.test import TestCase
from .models import Question
from django.core.urlresolvers import reverse

class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently()应该对 pub_date 字段是将来的那些问题返回false
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)
    def test_was_published_recently_with_old_question(self):
        """
        对于 pub_date 在一天以前的 Question，was_published_recently() 应该返回 False。
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        对于 pub_date 在一天之内的 Question，was_published_recently() 应该返回 True。
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    创建一个以 question_text 为标题，pub_date 为 days 天之后的问题。
    days 为正表示将来，为负表示过去。
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text,
                                   pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        如果数据库里木有投票，应该显示一个合适的提示信息。
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_index_view_with_a_past_question(self):
        """
        pub_date 值是过去的问题应该被显示在主页上。
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
                                 response.context['latest_question_list'],
                                 ['<Question: Past question.>']
                                 )
    
    def test_index_view_with_a_future_question(self):
        """
        pub_date 值是将来的问题不应该被显示在主页上。
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_index_view_with_future_question_and_past_question(self):
        """
        如果数据库里同时存在过去和将来的投票，那么只应该显示过去的那些。
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
                                 response.context['latest_question_list'],
                                 ['<Question: Past question.>']
                                 )
    
    def test_index_view_with_two_past_questions(self):
        """
        目录页应该可以显示多个投票。
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
                                 response.context['latest_question_list'],
                                 ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )
class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        访问将来发布的投票的详情页应该会收到一个 404 错误。
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        response = self.client.get(reverse('polls:detail',
                                                                             args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        访问过去发布的投票详情页，页面上应该显示投票标题。
        """
        past_question = create_question(question_text='Past Question.',
                                            days=-5)
        response = self.client.get(reverse('polls:detail',
                                                   args=(past_question.id,)))
        self.assertContains(response, past_question.question_text,
                                        status_code=200)
