# 필요한 라이브러리들을 불러옵니다.
import threading
import openai
import speech_recognition as sr
import pyttsx3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

# 안드로이드 권한 요청 (앱 실행 시 필요)
if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET])

class JarvisApp(App):

    def build(self):
        # --- UI (화면) 설정 ---
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        self.title_label = Label(
            text="AI 비서",
            font_size='32sp',
            bold=True
        )

        self.status_label = Label(
            text="아래 버튼을 눌러 대화를 시작하세요.",
            font_size='20sp'
        )

        self.run_button = Button(
            text="대화 시작",
            font_size='24sp',
            on_press=self.start_listening_thread
        )

        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.run_button)
        # --- UI 설정 끝 ---

        # --- AI 및 음성 기능 초기화 ---
        # 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
        # 예: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        self.api_key = "YOUR_OPENAI_API_KEY"
        
        # 음성 출력(TTS) 엔진 초기화
        self.tts_engine = pyttsx3.init()
        # --- 초기화 끝 ---

        return self.layout

    def start_listening_thread(self, instance):
        # "대화 시작" 버튼을 누르면 이 함수가 실행됩니다.
        # UI가 멈추지 않도록 새로운 스레드에서 음성 인식을 실행합니다.
        threading.Thread(target=self.listen_and_process).start()

    def listen_and_process(self):
        # 음성 인식 및 AI 처리의 전체 과정을 담당합니다.
        
        # 1. 상태 업데이트: "듣는 중..."
        self.update_status("듣고 있어요...")
        self.run_button.disabled = True # 버튼 비활성화

        # 2. 음성 인식 (STT)
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                self.update_status("음성 입력 시간이 초과되었습니다.\n다시 시도해주세요.")
                self.run_button.disabled = False
                return

        try:
            user_text = recognizer.recognize_google(audio, language='ko-KR')
            self.update_status(f"나: {user_text}")
        except sr.UnknownValueError:
            self.update_status("음성을 이해하지 못했어요. 다시 시도해주세요.")
            self.run_button.disabled = False
            return
        except sr.RequestError:
            self.update_status("네트워크 오류가 발생했습니다.")
            self.run_button.disabled = False
            return
            
        # 3. AI에게 질문하고 답변 받기
        self.update_status("생각 중...")
        try:
            openai.api_key = self.api_key
            response = openai.chat.completions.create(
                model="gpt-4o", # 최신 gpt-4o 모델 사용
                messages=[
                    {"role": "system", "content": "You are a helpful assistant named Jarvis."},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_response_text = response.choices[0].message.content
        except Exception as e:
            self.update_status(f"API 오류: {e}")
            self.run_button.disabled = False
            return

        # 4. AI 답변을 음성으로 출력 (TTS)
        self.update_status(f"AI: {ai_response_text}")
        self.speak(ai_response_text)
        
        # 모든 과정이 끝나면 버튼을 다시 활성화합니다.
        self.run_button.disabled = False


    def update_status(self, text):
        # UI 요소를 메인 스레드에서 안전하게 업데이트하기 위한 함수
        Clock.schedule_once(lambda dt: self._update_label(text))

    def _update_label(self, text):
        self.status_label.text = text

    def speak(self, text):
        # TTS 엔진을 사용해 텍스트를 음성으로 변환하여 말합니다.
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.update_status(f"음성 출력 오류: {e}")


if __name__ == '__main__':
    JarvisApp().run()
