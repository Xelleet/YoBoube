from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Video
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class VideoUploadTest(TestCase):
    def setUp(self):
        # Создаем клиента для тестирования
        self.client = Client()

        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Авторизуем пользователя
        self.client.login(username='testuser', password='testpassword')

    def test_upload_video(self):
        # Зайти на страницу upload_video
        response = self.client.get(reverse('upload_video'))
        self.assertEqual(response.status_code, 200)

        test_video = SimpleUploadedFile(
            name='test_video.mp4',
            content=b"file_content",
            content_type='video/mp4'
        )

        # Заполнить форму с данными
        data = {
            'title': 'Test Video Title',
            'author': self.user.id,  # Используем ID пользователя, а не объект
            'video_file': test_video
        }

        # Отправить данные на сервер
        response = self.client.post(reverse('upload_video'), data)
        self.assertEqual(response.status_code, 302)  # Ожидаем редирект после успешной загрузки

        # Проверить, что видео добавлено в базу данных
        self.assertEqual(Video.objects.count(), 1)
        video = Video.objects.first()
        self.assertEqual(video.uploader, self.user)  # Проверяем ID автора
        self.assertTrue(video.video_file.name.endswith('.mp4'))