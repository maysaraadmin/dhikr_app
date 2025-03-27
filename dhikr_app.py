from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.lang import Builder
from datetime import datetime, timedelta
import requests
import os
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Load RTL support
Builder.load_string('''
<RLabel@Label>:
    halign: 'right'
    text_size: self.width, None
    font_name: app.font_name
    padding_x: 20
''')

# Arabic text shaping and bidi support
def arabic_text(text):
    """Reshapes and applies Bidi algorithm to Arabic text."""
    return get_display(reshape(text))

# Load Arabic font
FONT_PATH = os.path.join(os.path.dirname(__file__), "Tajawal-Regular.ttf")
DEFAULT_FONT = 'Tajawal' if os.path.exists(FONT_PATH) else 'Arial'
if DEFAULT_FONT == 'Tajawal':
    LabelBase.register(name='Tajawal', fn_regular=FONT_PATH)

class DhikrApp(App):
    font_name = DEFAULT_FONT  # Global font access

    def build(self):
        self.title = arabic_text("تطبيق الأذكار")
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Scrollable layout for Azkar
        self.dhikr_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.dhikr_layout.bind(minimum_height=self.dhikr_layout.setter('height'))
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_view.add_widget(self.dhikr_layout)
        root.add_widget(scroll_view)

        # Button to calculate last third of the night
        calculate_button = Button(
            text=arabic_text("حساب الثلث الأخير من الليل"),
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_name=self.font_name
        )
        calculate_button.bind(on_press=self.calculate_last_third)
        root.add_widget(calculate_button)

        # Adding Azkar
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

        return root

    def add_dhikr(self, title, dhikr_list):
        """Adds a section of Azkar to the UI."""
        self.dhikr_layout.add_widget(Label(
            text=arabic_text(title),
            size_hint_y=None,
            height=50,
            font_size=20,
            color=[0.9, 0.9, 0, 1],  # Yellow color
            bold=True,
            font_name=self.font_name,
            halign='right',
            text_size=(self.dhikr_layout.width, None)
        ))

        for dhikr, count in dhikr_list:
            self.dhikr_layout.add_widget(Label(
                text=arabic_text(f"{dhikr} - {count} مرة"),
                size_hint_y=None,
                height=40,
                font_size=16,
                color=[0.8, 0.8, 0.8, 1],  # Gray color
                font_name=self.font_name,
                halign='right',
                text_size=(self.dhikr_layout.width, None)
            ))

    def fetch_prayer_times(self):
        """Fetches prayer times from the API."""
        params = {
            "latitude": 24.7136,
            "longitude": 46.6753,
            "timezone": "Asia/Riyadh",
            "method": 4
        }
        try:
            response = requests.get("http://api.pray.zone/v2/times/today.json", params=params)
            response.raise_for_status()  # Raise error for bad responses
            data = response.json()
            return data["results"]["datetime"][0]["times"]
        except (requests.RequestException, KeyError):
            return None

    def calculate_last_third(self, instance):
        """Calculates and displays the last third of the night."""
        prayer_times = self.fetch_prayer_times()
        if not prayer_times or "Maghrib" not in prayer_times or "Fajr" not in prayer_times:
            self.show_popup("خطأ", "فشل في جلب أوقات الصلاة")
            return

        today = datetime.now()
        maghrib_dt = datetime.combine(today.date(), datetime.strptime(prayer_times["Maghrib"], "%H:%M").time())
        fajr_dt = datetime.combine(today.date() + timedelta(days=1), datetime.strptime(prayer_times["Fajr"], "%H:%M").time())

        last_third_start = fajr_dt - (fajr_dt - maghrib_dt) / 3
        self.show_popup("الثلث الأخير من الليل", f"يبدأ الثلث الأخير من الليل في: {last_third_start.strftime('%H:%M')}")

    def show_popup(self, title, message):
        """Displays a popup with a given title and message."""
        popup = Popup(
            title=arabic_text(title),
            size_hint=(0.8, 0.4)
        )
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=arabic_text(message),
            color=[1, 1, 1, 1],
            font_size=18,
            font_name=self.font_name,
            halign='right',
            text_size=(None, None)
        ))
        close_button = Button(
            text=arabic_text("إغلاق"),
            size_hint=(1, 0.3),
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_name=self.font_name
        )
        close_button.bind(on_press=popup.dismiss)
        content.add_widget(close_button)
        popup.content = content
        popup.open()

if __name__ == '__main__':
    DhikrApp().run()
