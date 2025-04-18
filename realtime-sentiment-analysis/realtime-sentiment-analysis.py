import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import requests
import threading
import time
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from openai import AzureOpenAI

# .envファイルをロード
load_dotenv()

# Azure Speech-to-Text の設定
speech_subscription_key = os.getenv("SPEECH_SUBSCRIPTION_KEY")
speech_region = os.getenv("SPEECH_REGION")

# Azure Translator の設定
translator_subscription_key = os.getenv("TRANSLATOR_SUBSCRIPTION_KEY")
translator_endpoint = os.getenv("TRANSLATOR_ENDPOINT")
translator_region = os.getenv("TRANSLATOR_REGION")

# sentiment Analysis の設定
sentiment_analysis_endpoint = os.getenv("SENTIMENT_ANALYSIS_ENDPOINT")
sentiment_analysis_key = os.getenv("SENTIMENT_ANALYSIS_KEY")

# Azure Open AI の設定
aoai_endpoint = os.getenv("AOAI_ENDPOINT")
deployment = os.getenv("DEPLOYMENT")

aoai_key = os.getenv("AOAI_KEY")
api_version = os.getenv("API_VERSION")

# Azure Speech-to-Textでリアルタイムに日本語を認識する関数
def start_speech_recognition(should_stop):
    # 音声認識の設定
    speech_config = speechsdk.SpeechConfig(subscription=speech_subscription_key, region=speech_region)
    speech_config.speech_recognition_language = "ja-JP"  # 日本語の音声を認識
    
    # mic 入力
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)
    
    # wavファイルから音声認識
    # audio_config = speechsdk.audio.AudioConfig(filename="katiesteve.wav")

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    def recognized_callback(event):
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = event.result.text
            print(f"Recognized (Japanese): {text}")            
            dosuments = [text]  
            # Sentiment Analysis による感情分析
            docs = sentiment_analysis(dosuments)
            for idex, doc in enumerate(docs):
                print(f"Document text: {dosuments[idex]}")
                print(f"Sentiment Analysis sentiment: {doc.sentiment}")
            
            # Azure OpenAI による感情分析
            # respnse = openai(text)
            # print(f"OpenAI response: {respnse}")

        elif event.result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif event.result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = event.result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")

    # 音声認識のイベントハンドラを設定
    speech_recognizer.recognized.connect(recognized_callback)

    # 音声認識を非同期で開始
    print("Starting continuous recognition. Press Ctrl+C to stop...")
    speech_recognizer.start_continuous_recognition()

    # 停止条件が満たされるまで待機
    try:
        while not should_stop.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")

    # 音声認識を停止
    speech_recognizer.stop_continuous_recognition()

# 未使用　精度改善のため、日本語テキストから翻訳する場合に活用可能
# Azure Translatorで日本語テキストを英語に翻訳する関数
def translate_text(text, target_language="en"):
    path = '/translate'
    constructed_url = translator_endpoint + path

    params = {
        'api-version': '3.0',
        'to': target_language
    }

    headers = {
        'Ocp-Apim-Subscription-Key': translator_subscription_key,
        'Ocp-Apim-Subscription-Region': translator_region,
        'Content-type': 'application/json'
    }

    body = [{
        'text': text
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    if response:
        translated_text = response[0]['translations'][0]['text']
        return translated_text
    else:
        print("Translation failed.")
        return None

# Azure Language Service の Sentiment Analysis APIを使用して、テキストの感情を分析する関数
def sentiment_analysis(text):
    text_analytics_client = TextAnalyticsClient(endpoint=sentiment_analysis_endpoint, credential=AzureKeyCredential(sentiment_analysis_key))
    result = text_analytics_client.analyze_sentiment(text, show_opinion_mining=True)
    # return result
    
    if result:
        docs = [doc for doc in result if not doc.is_error]
        return docs
    else:
        print("Analysis failed.")
        return None

# Azure OpenAI Service を使用して、テキストの感情を分析する関数
# サンプルとして 5 段階で分類
def openai(text):
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=aoai_endpoint,
        api_key=aoai_key,
    )
    
    messages=[
        {"role": "system", "content": "感情を分析するアシスタントです。very positive, positive, neutral, negative, very negative の5つの感情を分析します。出力内容には、very positive, positive, neutral, negative, very negative のみを含み、他の情報は含めないでください。例 : very positive"},
        {"role": "user", "content": f"{text}"}
        ]

    response = client.chat.completions.create(  
        model=deployment,
        messages=messages,
        max_tokens=1000,  
    )
    
    return(response.choices[0].message.content)

# メイン処理
def main():
    should_stop = threading.Event()  # プログラム停止のフラグ

    # 音声認識と翻訳を別スレッドで実行
    recognition_thread = threading.Thread(target=start_speech_recognition, args=(should_stop,))
    recognition_thread.start()

    # プログラムを停止するにはCtrl+Cを押してください
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping translation...")
        should_stop.set()  # 停止フラグを立てる
        recognition_thread.join()  # スレッドの終了を待つ

# 実行部分
if __name__ == "__main__":
    main()
