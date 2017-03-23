from django.test import TestCase
from quiz.models import *
from django.contrib.auth.admin import User
import random


class TextQuestionTestCase(TestCase):

    def setUp(self):
        TextQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            answer = 'Answer',
        )

    def test_validation_ignores_capitalization(self):
        question = TextQuestion.objects.get()
        self.assertTrue(question.validate('ansWer'))
        question.answer = 'ANSWER'
        self.assertTrue(question.validate('ansWer'))

    def test_validation_ignores_special_characters(self):
        question = TextQuestion.objects.get()
        question.answer = 'this answer'
        self.assertTrue(question.validate('this-answer'))
        self.assertTrue(question.validate('this_answer'))
        self.assertTrue(question.validate('this.answer'))
        self.assertTrue(question.validate('this answer'))
        self.assertTrue(question.validate('thisanswer'))
        question.answer = 'this-answer'
        self.assertTrue(question.validate('this answer'))
        question.answer = 'this_answer'
        self.assertTrue(question.validate('this answer'))
        question.answer = 'thisanswer'
        self.assertTrue(question.validate('this answer'))

    def test_validation_not_ignores_numbers(self):
        question = TextQuestion.objects.get()
        question.answer = 'this answer'
        self.assertFalse(question.validate('this0answer'))
        question.answer = 'this answer1'
        self.assertFalse(question.validate('this answer'))


class NumberQuestionTestCase(TestCase):

    def setUp(self):
        NumberQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            answer = '1.000',
        )

    def test_empty_returns_false(self):
        question = NumberQuestion.objects.get()
        self.assertFalse(question.validate(''))

    def test_validation_of_correct_answer(self):
        question = NumberQuestion.objects.get()
        question.answer = '1231231.45'
        self.assertTrue(question.validate('1231231.45'))
        self.assertFalse(question.validate('12312314.5'))

    def test_validation_of_float_when_answer_is_int(self):
        question = NumberQuestion.objects.get()
        question.answer = '42'
        self.assertTrue(question.validate('42.0'))
        question.answer = 'AB'
        self.assertTrue(question.validate('AB.0'))

    def test_validation_of_comma_as_decimal_mark(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate('1.000'))
        self.assertTrue(question.validate('1,000'))

    def test_validation_of_superfluous_spaces(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate(' 1.000'))
        self.assertTrue(question.validate('1.000 '))
        self.assertTrue(question.validate(' 1.000 '))

    def test_validation_of_answer_without_decimal_part(self):
        question = NumberQuestion.objects.get()
        self.assertTrue(question.validate('1'))
        self.assertTrue(question.validate('1.'))


    def test_validation_of_answer_without_decimal_part_2(self):
        question = NumberQuestion.objects.get()
        question.answer = '133769'
        self.assertTrue(question.validate('133769'))
        self.assertTrue(question.validate('133769.'))
        self.assertFalse(question.validate('1.33769'))
        self.assertFalse(question.validate('1.3376.9'))


    def test_validation_of_answer_without_integer_part(self):
        question = NumberQuestion.objects.get()
        question.answer = '0.001'
        self.assertTrue(question.validate('.001'))
        question.answer = '1.001'
        self.assertFalse(question.validate('.001'))

    def test_validation_of_trailing_zeros(self):
        question = NumberQuestion.objects.get()
        question.answer = '0.1'
        self.assertTrue(question.validate('0.10'))
        self.assertFalse(question.validate('0.10010'))

    def test_validation_of_zero(self):
        question = NumberQuestion.objects.get()
        question.answer = '0'
        self.assertTrue(question.validate('0'))
        self.assertTrue(question.validate('0.'))
        self.assertTrue(question.validate('.'))
        self.assertTrue(question.validate('.0'))

    def test_validation_of_leading_zeroes(self):
        question = NumberQuestion.objects.get()
        question.answer = '10'
        self.assertTrue(question.validate('010'))

    def test_validation_of_hexadecimal_capitalization(self):
        question = NumberQuestion.objects.get()
        question.answer = 'aB3.bF1'
        self.assertTrue(question.validate('ab3.bf1'))
        self.assertTrue(question.validate('AB3.BF1'))
        self.assertTrue(question.validate('Ab3.Bf1'))
        question.answer = 'AB123ef'
        self.assertTrue(question.validate('Ab123eF'))


class MultipleChoiceTestCase(TestCase):

    def setUp(self):
        question = MultipleChoiceQuestion.objects.create(
            question_text = 'TEST_QUESTION',
        )
        answers = [MultipleChoiceAnswer.objects.create(
                question = question,
                answer = 'TEST_ANSWER_%s' % ans,
                correct = False,
            ) for ans in ('A', 'B', 'C', 'D')]
        trueAnswer = answers[random.randint(0,3)]
        trueAnswer.correct = True
        trueAnswer.save()


    def testAnswerCorrect(self):
        question = MultipleChoiceQuestion.objects.get(question_text='TEST_QUESTION')
        correctAnswers = MultipleChoiceAnswer.objects.filter(
            question = question,
            correct = True,
        )
        correctAnswer = correctAnswers[0]
        response = question.answerFeedback(correctAnswer.id)
        json = {
            'answer': correctAnswer.id,
            'correct': [correctAnswer.id for correctAnswer in correctAnswers],
            'answeredCorrect': True,
        }
        self.assertEqual(response, json)

    def testAnswerIncorrect(self):
        question = MultipleChoiceQuestion.objects.get(question_text='TEST_QUESTION')
        wrongAnswers = MultipleChoiceAnswer.objects.filter(
            question = question,
            correct = False,
            )
        correctAnswers = MultipleChoiceAnswer.objects.filter(
            question = question,
            correct = True,
            )
        wrongAnswer = wrongAnswers[0]
        response = question.answerFeedback(wrongAnswer.id)
        json = {
            'answer': wrongAnswer.id,
            'correct': [correctAnswer.id for correctAnswer in correctAnswers],
            'answeredCorrect': False,
        }
        self.assertEqual(response, json)


class TrueFalseTestCase(TestCase):

    def setUp(self):
        TrueFalseQuestion.objects.create(
            question_text = 'TEST_QUESTION',
            answer = True,
        )

    def testAnswerCorrect(self):
        question = TrueFalseQuestion.objects.get(question_text='TEST_QUESTION')
        response = question.answerFeedback(True)
        json = {
            'answer': True,
            'correct': True,
            'answeredCorrect': True,
        }
        self.assertEqual(response, json)

    def testAnswerIncorrect(self):
        question = TrueFalseQuestion.objects.get(question_text='TEST_QUESTION')
        response = question.answerFeedback(False)
        json = {
            'answer': False,
            'correct': True,
            'answeredCorrect': False,
        }
        self.assertEqual(response, json)



class RatingTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(

        )
        player = Player.objects.create(
            rating=1000,
            user=user,
        )
        category = Category.objects.create(
            title="test_category",
        )
        subject = Subject.objects.create(
            title="test_subject",
            category=category,
        )
        topic = Topic.objects.create(
            title="test_topic",
            subject=subject,
        )
        question = Question.objects.create(
            rating=1000,
            topic=topic,
        )

    def test_rating_change_on_correct(self):
        player = Player.objects.get()
        question = Question.objects.get()
        player.update(question, 1)
        self.assertTrue(question.rating < 1000)
        self.assertTrue(player.rating > 1000)

    def test_rating_change_on_incorrect(self):
        player = Player.objects.get()
        question = Question.objects.get()
        player.update(question, 0)
        self.assertTrue(question.rating > 1000)
        self.assertTrue(player.rating < 1000)

    def test_no_rating_change_above_cap(self):
        player = Player.objects.get()
        player.rating = 1500
        question = Question.objects.get()
        player.update(question, 0)
        self.assertTrue(question.rating == 1000)
        self.assertTrue(player.rating == 1500)

    def test_virtual_rating_increase(self):
        player = Player.objects.get()
        question = Question.objects.get()
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=True,
        )
        self.assertTrue(player.rating < player.virtualRating([question.topic]))

    def test_virtual_rating_decrease(self):
        player = Player.objects.get()
        question = Question.objects.get()
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=False,
        )
        self.assertTrue(player.rating > player.virtualRating([question.topic]))

    def test_virtual_rating_increase_and_decrease(self):
        player = Player.objects.get()
        question = Question.objects.get()
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=True,
        )
        PlayerAnswer.objects.create(
            player=player,
            question=question,
            result=False,
        )
        self.assertTrue(player.rating == player.virtualRating([question.topic]))

class AchievementTestCase(TestCase):

    def setUp(self):
        achievement = Achievement.objects.create(name='TEST_ACHIEVEMENT')
        prop = Property.objects.create(name='TEST_PROPERTY')
        trigger = Trigger.objects.create(name='TEST_TRIGGER')
        title = Title.objects.create(title='TEST_TITLE')
        user = User.objects.create(username='TEST_USER')
        Player.objects.create(user=user)

        trigger.properties.add(prop)
        prop.achievements.add(achievement)
        title.achievement = achievement

        trigger.save()
        prop.save()
        title.save()

    def testName(self):
        achievement = Achievement.objects.get()
        self.assertEqual(str(achievement), 'TEST_ACHIEVEMENT')

    def testTrigger(self):
        player = Player.objects.get()
        prop = Property.objects.get(name='TEST_PROPERTY')

        Trigger.objects.get(name='TEST_TRIGGER').trigger(player)

        propertyUnlocks = PropertyUnlock.objects.filter(player=player, prop=prop)

        self.assertEqual(propertyUnlocks.count(), 1)

    def testAchieve(self):
        player = Player.objects.get()
        achievement = Achievement.objects.get(name='TEST_ACHIEVEMENT')

        Trigger.objects.get(name='TEST_TRIGGER').trigger(player)

        achievementUnlock = AchievementUnlock.objects.filter(player=player, achievement=achievement)

        self.assertEqual(achievementUnlock.count(), 1)

    def testTitle(self):
        player = Player.objects.get()
        title = Title.objects.get(title='TEST_TITLE')

        Trigger.objects.get(name='TEST_TRIGGER').trigger(player)

        titleUnlock = TitleUnlock.objects.filter(player=player, title=title)

        self.assertEqual(titleUnlock.count(), 1)


class TitleTestCase(TestCase):

    def setUp(self):
        achievement = Achievement.objects.create(name='TEST_ACHIEVEMENT')
        Title.objects.create(
            title = 'TEST_TITLE',
            achievement = achievement,
        )

    def test_str_returns_title(self):
        title = Title.objects.get()
        self.assertEqual(str(title), 'TEST_TITLE')


class PlayerTestCase(TestCase):

    def setUp(self):
        user = User.objects.create(username='TEST_USER')
        Player.objects.create(user=user)

    def test_str_returns_username(self):
        player =  Player.objects.get()
        self.assertEqual(str(player), 'TEST_USER')


class PropertyTestCase(TestCase):

    def setUp(self):
        Property.objects.create(name='TEST_PROPERTY')

    def test_str_returns_name(self):
        prop = Property.objects.get()
        self.assertEqual(str(prop), 'TEST_PROPERTY')


class TriggerTestCase(TestCase):

    def setUp(self):
        Trigger.objects.create(name='TEST_TRIGGER')

    def test_str_returns_name(self):
        trigger = Trigger.objects.get()
        self.assertEqual(str(trigger), 'TEST_TRIGGER')


class CategoryTestCase(TestCase):

    def setUp(self):
        Category.objects.create(title='TEST_CATEGORY')

    def test_str_returns_name(self):
        cat = Category.objects.get()
        self.assertEqual(str(cat), 'TEST_CATEGORY')


class SubjectTestCase(TestCase):

    def setUp(self):
        cat = Category.objects.create(title='TEST_CATEGORY')
        Subject.objects.create(
            title='TEST_SUBJECT',
            short='TS',
            code='TS1234',
            category=cat,
        )

    def test_str_returns_code_and_title(self):
        sub = Subject.objects.get()
        self.assertEqual(str(sub), 'TS1234 - TEST_SUBJECT')

class TopicTestCase(TestCase):

    def setUp(self):
        cat = Category.objects.create(title='TEST_CATEGORY')
        sub = Subject.objects.create(
            title='TEST_SUBJECT',
            short='TSUB',
            code='TS1234',
            category=cat,
        )
        Topic.objects.create(
            title='TEST_TOPIC',
            subject=sub,
        )

    def test_str_returns_name(self):
        topic = Topic.objects.get()
        self.assertEqual(str(topic), 'TEST_TOPIC')


class QuestionTestCase(TestCase):

    def setUp(self):
        Question.objects.create(question_text='TEST_QUESTION')

    def test_str_returns_name(self):
        q = Question.objects.get()
        self.assertEqual(str(q), 'TEST_QUESTION')


class MultipleChoiceAnswerTestCase(TestCase):

    def setUp(self):
        mc = MultipleChoiceQuestion.objects.create(
            question_text='TEST_MC'

        )
        MultipleChoiceAnswer.objects.create(question=mc, answer='TEST_MC_ANS', correct=True)

    def test_str_returns_name(self):
        mca = MultipleChoiceAnswer.objects.get()
        self.assertEqual(str(mca), 'TEST_MC_ANS')


