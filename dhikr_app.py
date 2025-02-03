from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from datetime import datetime, timedelta
import requests


class DhikrApp(App):
    def build(self):
        self.title = "تطبيق الأذكار"
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # واجهة الأذكار
        self.dhikr_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.dhikr_layout.bind(minimum_height=self.dhikr_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 0.8))
        scroll_view.add_widget(self.dhikr_layout)
        self.root.add_widget(scroll_view)

        # زر لحساب الثلث الأخير من الليل
        self.calculate_button = Button(
            text="حساب الثلث الأخير من الليل",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.calculate_button.bind(on_press=self.calculate_last_third)
        self.root.add_widget(self.calculate_button)

        # إضافة الأذكار
        self.add_dhikr("أذكار الصباح", [
            ("سبحان الله وبحمده", 100),
            ("لا إله إلا الله وحده لا شريك له", 10),
            ("أستغفر الله وأتوب إليه", 100),
            ("اللهم بك أصبحنا وبك أمسينا", 1),
            ("أعوذ بكلمات الله التامات من شر ما خلق", 3)
        ])

        self.add_dhikr("أذكار المساء", [
            ("سبحان الله وبحمده", 100),
            ("لا إله إلا الله وحده لا شريك له", 10),
            ("أستغفر الله وأتوب إليه", 100),
            ("اللهم بك أمسينا وبك أصبحنا", 1),
            ("أعوذ بكلمات الله التامات من شر ما خلق", 3)
        ])

        self.add_dhikr("أذكار بعد الصلوات", [
            ("أستغفر الله", 3),
            ("اللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام", 1),
            ("لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير", 10)
        ])

        return self.root

    def add_dhikr(self, title, dhikr_list):
        self.dhikr_layout.add_widget(Label(
            text=title,
            size_hint_y=None,
            height=40,
            font_size=20,
            color=[0.9, 0.9, 0, 1],  # لون أصفر
            bold=True
        ))
        for dhikr, count in dhikr_list:
            dhikr_label = Label(
                text=f"{dhikr} - {count} مرة",
                size_hint_y=None,
                height=40,
                font_size=16,
                color=[0.8, 0.8, 0.8, 1]  # لون رمادي
            )
            self.dhikr_layout.add_widget(dhikr_label)

    def calculate_last_third(self, instance):
        # الحصول على أوقات الصلاة باستخدام API
        try:
            # بيانات الموقع (يمكن تغييرها لتناسب موقع المستخدم)
            params = {
                "latitude": 24.7136,
                "longitude": 46.6753,
                "timezone": "Asia/Riyadh",
                "method": 4  # طريقة الحساب (مثلاً: جامعة أم القرى)
            }
            response = requests.get("http://api.pray.zone/v2/times/today.json", params=params)
            prayer_times = response.json()["results"]["datetime"][0]["times"]

            maghrib_time = datetime.strptime(prayer_times["Maghrib"], "%H:%M")
            fajr_time = datetime.strptime(prayer_times["Fajr"], "%H:%M")

            # حساب الفترة بين المغرب والفجر
            night_duration = fajr_time - maghrib_time
            third_duration = night_duration / 3

            # حساب الثلث الأخير
            last_third_start = fajr_time - third_duration

            # عرض النتيجة
            popup = Popup(
                title='الثلث الأخير من الليل',
                size_hint=(0.8, 0.4),
                title_color=[1, 1, 1, 1],
                title_size=20,
                background_color=[0.2, 0.2, 0.2, 1]
            )
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            content.add_widget(Label(
                text=f"يبدأ الثلث الأخير من الليل في: {last_third_start.strftime('%H:%M')}",
                color=[1, 1, 1, 1],
                font_size=18
            ))
            close_button = Button(
                text="إغلاق",
                size_hint=(1, 0.3),
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            close_button.bind(on_press=popup.dismiss)
            content.add_widget(close_button)
            popup.content = content
            popup.open()

        except Exception as e:
            # عرض رسالة خطأ في حالة فشل الاتصال بالـ API
            popup = Popup(
                title='خطأ',
                size_hint=(0.8, 0.4),
                title_color=[1, 1, 1, 1],
                title_size=20,
                background_color=[0.2, 0.2, 0.2, 1]
            )
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            content.add_widget(Label(
                text="فشل في الحصول على أوقات الصلاة. يرجى التحقق من اتصال الإنترنت.",
                color=[1, 1, 1, 1],
                font_size=18
            ))
            close_button = Button(
                text="إغلاق",
                size_hint=(1, 0.3),
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            close_button.bind(on_press=popup.dismiss)
            content.add_widget(close_button)
            popup.content = content
            popup.open()

if __name__ == '__main__':
    DhikrApp().run()