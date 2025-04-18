## リアルタイム感情分析サンプル
Azure AI Searvice の Speach、Language、Azure OpenAI を用いたサンプルで、
リアルタイムで音声入力を Speech to Text によって文字起こしし、Sentiment Analysis で感情分析を行う。
Azure OpenAI Service にテキストを渡し、感情分析を行うことも可能。

### 手順

1. Azure AI Searvice のデプロイ

Azure AI Searvice を以下の手順でデプロイ  
https://learn.microsoft.com/ja-jp/azure/ai-services/multi-service-resource?pivots=azportal


2. .env ファイルの作成
.env.example を参考に作成環境の情報に編集 

```
# Azure Speech-to-Text の設定
SPEECH_SUBSCRIPTION_KEY = 
SPEECH_REGION = 

# Azure Translator の設定
TRANSLATOR_SUBSCRIPTION_KEY = 
TRANSLATOR_ENDPOINT = 
TRANSLATOR_REGION = 

# sentiment Analysis の設定
SENTIMENT_ANALYSIS_ENDPOINT = 
SENTIMENT_ANALYSIS_KEY = 

# Azure Open AI の設定
AOAI_ENDPOINT = 
DEPLOYMENT = 

AOAI_KEY = 
API_VERSION = 
```


3. パッケージのインストール

```bash
pip install -r requirements.txt
```